"""
Valuation engine: computes a wear-aware resale price estimate from persisted market comps.

Algorithm steps (each independently reviewable):
  1. Filter comps below a similarity threshold
  2. Remove price outliers via IQR
  3. Compute similarity-weighted average price
  4. Apply a condition discount multiplier
  5. Apply a conservative visible-wear adjustment
  6. Derive low / mid / high bounds
  7. Set confidence and reason from comp count + avg similarity + wear
"""

# Comps below this similarity are too irrelevant to use.
# Fall back to all comps if fewer than 2 survive the filter.
_MIN_SIMILARITY = 0.2

# Condition multipliers reflect the resale discount vs. a reference market price.
_CONDITION_MULTIPLIERS: dict[str, float] = {
    "new": 1.0,
    "like_new": 0.90,
    "good": 0.78,
    "fair": 0.60,
    "poor": 0.40,
}
_DEFAULT_CONDITION_MULTIPLIER = 0.75  # used when condition is unknown

# Minimum wear_confidence to apply any wear adjustment.
# Below this threshold the image evidence is too weak to adjust pricing.
_MIN_WEAR_CONFIDENCE = 0.40

# Maximum wear penalty we allow, expressed as a fraction reduction.
# Caps at 15% so a single uncertain assessment never tanks the price.
_MAX_WEAR_PENALTY = 0.15


def _get_wear_adjustment(item: dict) -> tuple[float, str | None]:
    """
    Returns (adjustment_factor, wear_description_for_reason).
    Factor is between (1 - _MAX_WEAR_PENALTY) and 1.0.
    Returns (1.0, None) when wear is unknown, none, or low-confidence.
    """
    metadata = item.get("extracted_metadata_json") or {}
    wear = metadata.get("wear_assessment")
    if not wear:
        return 1.0, None

    wear_level = (wear.get("wear_level") or "unknown").lower()
    wear_confidence = float(wear.get("wear_confidence") or 0)
    raw_factor = float(wear.get("pricing_adjustment_factor") or 1.0)

    # No adjustment for unknown/none wear or low-confidence assessments
    if wear_level in ("none", "unknown") or wear_confidence < _MIN_WEAR_CONFIDENCE:
        return 1.0, None

    # Scale the discount by confidence to stay conservative.
    # e.g., raw_factor=0.85 (15% off), confidence=0.65 → penalty = 0.15 * 0.65 = 0.0975
    raw_penalty = 1.0 - raw_factor
    scaled_penalty = raw_penalty * wear_confidence
    # Cap at max allowed penalty
    capped_penalty = min(scaled_penalty, _MAX_WEAR_PENALTY)
    adjusted_factor = round(1.0 - capped_penalty, 4)

    level_labels = {
        "light": "light visible wear",
        "moderate": "moderate visible wear",
        "heavy": "heavy visible wear",
    }
    description = level_labels.get(wear_level)
    if description is None:
        return 1.0, None

    return adjusted_factor, description


def compute_valuation(item: dict, comps: list[dict]) -> dict:
    """
    Returns a valuation dict ready for persistence.
    Raises ValueError if valuation cannot be computed (e.g. no usable comps).

    `comps` should be raw DB rows from the market_comps table, containing
    `comp_price` (float) and `similarity_score` (float).
    """
    if not comps:
        raise ValueError("No comparable listings are available for this item.")

    # Step 1 — filter by similarity
    strong = [c for c in comps if (c.get("similarity_score") or 0) >= _MIN_SIMILARITY]
    working = strong if len(strong) >= 2 else comps

    # Extract prices and paired similarity scores
    pairs: list[tuple[float, float]] = []
    for c in working:
        price = c.get("comp_price") or c.get("price")
        sim = c.get("similarity_score") or 0.5
        if price and price > 0:
            pairs.append((float(price), float(sim)))

    if not pairs:
        raise ValueError("No valid prices found in comparable listings.")

    # Step 2 — IQR outlier removal (only meaningful with ≥ 4 prices)
    if len(pairs) >= 4:
        pairs = _remove_outliers(pairs)
        if not pairs:
            pairs = [(float(c.get("comp_price") or 0), float(c.get("similarity_score") or 0.5))
                     for c in working if (c.get("comp_price") or 0) > 0]

    prices = [p for p, _ in pairs]
    similarities = [s for _, s in pairs]

    # Step 3 — similarity-weighted average (market reference price)
    total_weight = sum(similarities)
    if total_weight > 0:
        weighted_avg = sum(p * s for p, s in pairs) / total_weight
    else:
        weighted_avg = sum(prices) / len(prices)

    # Step 4 — condition adjustment
    condition = (item.get("condition") or "").lower().strip()
    factor = _CONDITION_MULTIPLIERS.get(condition, _DEFAULT_CONDITION_MULTIPLIER)

    # Step 5 — visible wear adjustment (conservative, image-based only)
    wear_factor, wear_desc = _get_wear_adjustment(item)

    mid = round(weighted_avg * factor * wear_factor, 2)

    # Step 6 — low / high bounds from the spread of adjusted prices
    adjusted = sorted(p * factor * wear_factor for p in prices)
    n = len(adjusted)

    if n >= 2:
        low_idx = max(0, int(n * 0.25))
        high_idx = min(n - 1, int(n * 0.75))
        low = round(adjusted[low_idx] * 0.92, 2)
        high = round(adjusted[high_idx] * 1.08, 2)
    else:
        low = round(mid * 0.80, 2)
        high = round(mid * 1.20, 2)

    # Guarantee ordering
    low = min(low, mid)
    high = max(high, mid)

    # Suggested listing price — slightly below mid to be competitive, never below low
    suggested = max(round(mid * 0.97, 2), low)

    # Step 7 — confidence and reason
    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
    comp_count = len(prices)
    confidence, reason = _confidence_and_reason(comp_count, avg_sim, wear_desc)

    valuation_method = "comp_weighted_heuristic"
    if wear_factor < 1.0:
        valuation_method = "comp_weighted_wear_adjusted_heuristic"

    return {
        "estimated_low": low,
        "estimated_mid": mid,
        "estimated_high": high,
        "suggested_listing_price": suggested,
        "confidence": confidence,
        "valuation_reason": reason,
        "valuation_method": valuation_method,
        "comp_count": comp_count,
    }


def _remove_outliers(
    pairs: list[tuple[float, float]],
) -> list[tuple[float, float]]:
    """IQR-based outlier removal. Returns original list if filter is too aggressive."""
    prices = sorted(p for p, _ in pairs)
    n = len(prices)
    q1 = prices[n // 4]
    q3 = prices[(3 * n) // 4]
    iqr = q3 - q1
    if iqr == 0:
        return pairs
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    filtered = [(p, s) for p, s in pairs if lower <= p <= upper]
    return filtered if len(filtered) >= 2 else pairs


def _confidence_and_reason(
    comp_count: int, avg_similarity: float, wear_desc: str | None
) -> tuple[str, str]:
    wear_clause = f" Adjusted conservatively for {wear_desc} shown in the provided photos." if wear_desc else ""

    if comp_count >= 5 and avg_similarity >= 0.50:
        return (
            "high",
            f"Based on {comp_count} strong comparable market listings.{wear_clause}",
        )
    if comp_count >= 3 or (comp_count >= 2 and avg_similarity >= 0.35):
        return (
            "medium",
            f"Based on {comp_count} comparable listing{'s' if comp_count != 1 else ''} "
            f"with moderate similarity.{wear_clause}",
        )
    plural = "s" if comp_count != 1 else ""
    return (
        "low",
        f"Based on {comp_count} comparable listing{plural}. "
        f"Estimate has higher uncertainty due to limited exact matches.{wear_clause}",
    )
