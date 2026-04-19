import re
from serpapi import GoogleSearch
from app.core import config


def search_comps(item: dict) -> tuple[list[dict], dict]:
    """
    Returns (normalized_comps, search_strategy_info).
    Tries queries in priority order and returns results from the first successful one.
    """
    config.require_serpapi()

    queries = _build_queries(item)
    search_strategy = {
        "primary_query": queries[0] if queries else "",
        "fallback_query": queries[1] if len(queries) > 1 else None,
        "source": "serpapi",
    }

    for query in queries:
        raw_results = _serpapi_search(query)
        if raw_results:
            comps = _normalize_and_filter(raw_results, item)
            if comps:
                search_strategy["used_query"] = query
                return comps[:10], search_strategy

    search_strategy["used_query"] = queries[0] if queries else ""
    return [], search_strategy


def _build_queries(item: dict) -> list[str]:
    brand = (item.get("brand") or "").strip()
    title = (item.get("title_guess") or "").strip()
    category = (item.get("category") or "").strip()
    item_type = (item.get("item_type") or "").strip()

    queries: list[str] = []

    # 1. exact: brand + title_guess
    if brand and title:
        q = f"{brand} {title}"
        if q not in queries:
            queries.append(q)

    # 2. broader: just title_guess
    if title and title not in queries:
        queries.append(title)

    # 3. brand + item_type
    if brand and item_type:
        q = f"{brand} {item_type}"
        if q not in queries:
            queries.append(q)

    # 4. item_type + category fallback
    if item_type and category:
        q = f"{item_type} {category}"
        if q not in queries:
            queries.append(q)
    elif category and category not in queries:
        queries.append(category)

    return queries or ["used item for sale"]


def _serpapi_search(query: str) -> list[dict]:
    try:
        search = GoogleSearch({
            "q": query,
            "engine": "google_shopping",
            "api_key": config.SERPAPI_API_KEY,
            "num": 20,
            "gl": "us",
            "hl": "en",
        })
        results = search.get_dict()
        return results.get("shopping_results", [])
    except Exception as exc:
        print(f"[market_data_service] SerpApi search failed for query '{query}': {exc}")
        return []


def _parse_price(price_str: str | None) -> float | None:
    if not price_str:
        return None
    # Remove currency symbols and commas; handle ranges like "$50.00 - $80.00" → take lower
    match = re.search(r"\d+(?:,\d{3})*(?:\.\d+)?", str(price_str).replace(",", ""))
    if match:
        try:
            return float(match.group().replace(",", ""))
        except ValueError:
            return None
    return None


_STOP_WORDS = {
    "a", "an", "the", "for", "and", "or", "of", "in", "on", "at", "to",
    "pre", "used", "with", "mens", "womens", "men", "women", "size", "new",
    "s", "m", "l", "xl",
}


def _score_similarity(comp_title: str, item: dict) -> float:
    """Word-overlap similarity between a comp title and the extracted item metadata."""
    comp_words = set(comp_title.lower().split()) - _STOP_WORDS

    reference_words: set[str] = set()
    for field in ["title_guess", "brand", "category", "item_type", "color"]:
        val = item.get(field) or ""
        reference_words.update(val.lower().split())
    reference_words -= _STOP_WORDS

    if not reference_words:
        return 0.5

    overlap = len(comp_words & reference_words)
    score = overlap / len(reference_words)
    return min(round(score, 2), 1.0)


def _normalize_and_filter(raw_results: list[dict], item: dict) -> list[dict]:
    comps = []
    for r in raw_results:
        price = _parse_price(r.get("price"))
        if price is None or price <= 0:
            continue

        title = (r.get("title") or "").strip()
        if not title:
            continue

        url = r.get("link") or r.get("product_link") or ""

        comp = {
            "source": "serpapi",
            "title": title,
            "price": price,
            "currency": "USD",
            "url": url,
            "image_url": r.get("thumbnail"),
            "condition": r.get("condition"),
            "similarity_score": _score_similarity(title, item),
            "raw_json": r,
        }
        comps.append(comp)

    comps.sort(key=lambda c: c["similarity_score"], reverse=True)
    return comps
