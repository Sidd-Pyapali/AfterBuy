"""
Valuation engine: computes a resale price estimate from persisted market comps.

Algorithm steps (each independently reviewable):
  1. Filter comps below a similarity threshold
  2. Remove price outliers via IQR
  3. Compute similarity-weighted average price
  4. Apply a condition discount multiplier
  5. Derive low / mid / high bounds
  6. Set confidence and reason from comp count + avg similarity
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
            # Edge case: IQR removed everything; use originals
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

    mid = round(weighted_avg * factor, 2)

    # Step 5 — low / high bounds from the spread of adjusted prices
    adjusted = sorted(p * factor for p in prices)
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

    # Step 6 — confidence and reason
    avg_sim = sum(similarities) / len(similarities) if similarities else 0.0
    comp_count = len(prices)
    confidence, reason = _confidence_and_reason(comp_count, avg_sim)

    return {
        "estimated_low": low,
        "estimated_mid": mid,
        "estimated_high": high,
        "suggested_listing_price": suggested,
        "confidence": confidence,
        "valuation_reason": reason,
        "valuation_method": "comp_weighted_heuristic",
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
    # If all prices are identical, IQR is 0 — skip filtering
    if iqr == 0:
        return pairs
    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr
    filtered = [(p, s) for p, s in pairs if lower <= p <= upper]
    return filtered if len(filtered) >= 2 else pairs


def _confidence_and_reason(comp_count: int, avg_similarity: float) -> tuple[str, str]:
    if comp_count >= 5 and avg_similarity >= 0.50:
        return (
            "high",
            f"Based on {comp_count} strong comparable market listings.",
        )
    if comp_count >= 3 or (comp_count >= 2 and avg_similarity >= 0.35):
        return (
            "medium",
            f"Based on {comp_count} comparable listing{'s' if comp_count != 1 else ''} "
            "with moderate similarity.",
        )
    plural = "s" if comp_count != 1 else ""
    return (
        "low",
        f"Based on {comp_count} comparable listing{plural}. "
        "Estimate has higher uncertainty due to limited exact matches.",
    )
