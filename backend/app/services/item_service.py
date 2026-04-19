from typing import Any
from app.core.supabase_client import get_supabase


def create_item(image_url: str, source_type: str = "photo", input_text: str | None = None) -> dict:
    client = get_supabase()
    result = client.table("items").insert({
        "image_url": image_url,
        "source_type": source_type,
        "input_text": input_text,
    }).execute()
    return result.data[0]


def update_item_extraction(item_id: str, extraction: dict) -> dict:
    client = get_supabase()
    result = client.table("items").update({
        "brand": extraction.get("brand"),
        "category": extraction.get("category"),
        "item_type": extraction.get("item_type"),
        "title_guess": extraction.get("likely_product_name"),
        "color": extraction.get("color"),
        "condition": extraction.get("visible_condition"),
        "confidence_score": extraction.get("confidence"),
        "extracted_metadata_json": extraction,
    }).eq("id", item_id).execute()
    return result.data[0]


def insert_comps(item_id: str, comps: list[dict]) -> list[dict]:
    if not comps:
        return []
    client = get_supabase()
    rows = [
        {
            "item_id": item_id,
            "source": c.get("source"),
            "comp_title": c.get("title"),
            "comp_price": c.get("price"),
            "currency": c.get("currency", "USD"),
            "comp_url": c.get("url"),
            "comp_condition": c.get("condition"),
            "comp_image_url": c.get("image_url"),
            "similarity_score": c.get("similarity_score"),
            "raw_json": c.get("raw_json"),
        }
        for c in comps
    ]
    result = client.table("market_comps").insert(rows).execute()
    return result.data


def insert_valuation(item_id: str, valuation: dict) -> dict:
    client = get_supabase()
    result = client.table("valuations").insert({
        "item_id": item_id,
        "estimated_low": valuation.get("estimated_low"),
        "estimated_mid": valuation.get("estimated_mid"),
        "estimated_high": valuation.get("estimated_high"),
        "suggested_listing_price": valuation.get("suggested_listing_price"),
        "confidence": valuation.get("confidence"),
        "valuation_reason": valuation.get("valuation_reason"),
        "valuation_method": valuation.get("valuation_method"),
        "comp_count": valuation.get("comp_count"),
    }).execute()
    return result.data[0]


def update_listing(listing_id: str, fields: dict) -> dict:
    client = get_supabase()
    result = client.table("generated_listings").update(fields).eq("id", listing_id).execute()
    if not result.data:
        raise ValueError(f"Listing {listing_id} not found")
    return result.data[0]


def insert_publications(item_id: str, publications: list[dict]) -> list[dict]:
    if not publications:
        return []
    client = get_supabase()
    rows = [
        {
            "item_id": item_id,
            "platform": p["platform"],
            "publication_status": p["publication_status"],
            "external_listing_id": p.get("external_listing_id"),
            "external_listing_url": p.get("external_listing_url"),
            "raw_response_json": p.get("raw_response_json"),
        }
        for p in publications
    ]
    result = client.table("listing_publications").insert(rows).execute()
    return result.data


def insert_generated_listing(item_id: str, listing: dict) -> dict:
    client = get_supabase()
    result = client.table("generated_listings").insert({
        "item_id": item_id,
        "platform": listing.get("platform", "generic"),
        "title": listing.get("title"),
        "description": listing.get("description"),
        "condition_note": listing.get("condition_note"),
        "suggested_price": listing.get("suggested_price"),
        "attributes_json": listing.get("attributes"),
        "generation_reasoning": listing.get("generation_reasoning"),
    }).execute()
    return result.data[0]


def get_items_list(limit: int = 20, offset: int = 0) -> list[dict]:
    client = get_supabase()

    items_result = (
        client.table("items")
        .select("id, created_at, image_url, title_guess, category, brand, item_type")
        .order("created_at", desc=True)
        .limit(limit)
        .offset(offset)
        .execute()
    )
    items = items_result.data or []
    if not items:
        return []

    item_ids = [i["id"] for i in items]

    val_result = (
        client.table("valuations")
        .select("item_id, estimated_mid")
        .in_("item_id", item_ids)
        .order("created_at", desc=True)
        .execute()
    )
    # keep only the latest valuation per item
    seen: set[str] = set()
    val_map: dict[str, float | None] = {}
    for v in (val_result.data or []):
        iid = v["item_id"]
        if iid not in seen:
            val_map[iid] = v["estimated_mid"]
            seen.add(iid)

    pub_result = (
        client.table("listing_publications")
        .select("item_id, platform, publication_status")
        .in_("item_id", item_ids)
        .execute()
    )
    pub_map: dict[str, list[dict]] = {}
    for p in (pub_result.data or []):
        iid = p["item_id"]
        pub_map.setdefault(iid, []).append(p)

    listing_result = (
        client.table("generated_listings")
        .select("item_id, title")
        .in_("item_id", item_ids)
        .order("created_at", desc=True)
        .execute()
    )
    listing_seen: set[str] = set()
    listing_map: dict[str, str | None] = {}
    for l in (listing_result.data or []):
        iid = l["item_id"]
        if iid not in listing_seen:
            listing_map[iid] = l.get("title")
            listing_seen.add(iid)

    enriched = []
    for item in items:
        iid = item["id"]
        pubs = pub_map.get(iid, [])
        platforms = [p["platform"] for p in pubs]
        enriched.append({
            "id": iid,
            "created_at": item["created_at"],
            "image_url": item["image_url"],
            "title_guess": item.get("title_guess"),
            "listing_title": listing_map.get(iid),
            "category": item.get("category"),
            "brand": item.get("brand"),
            "item_type": item.get("item_type"),
            "valuation_mid": val_map.get(iid),
            "platforms": platforms,
            "listing_status": "distributed" if platforms else ("listed" if iid in listing_map else ("valued" if iid in val_map else "identified")),
        })
    return enriched


def get_assembled_item(item_id: str) -> dict | None:
    client = get_supabase()

    item_result = client.table("items").select("*").eq("id", item_id).execute()
    if not item_result.data:
        return None
    item = item_result.data[0]

    comps_result = (
        client.table("market_comps")
        .select("*")
        .eq("item_id", item_id)
        .order("similarity_score", desc=True)
        .execute()
    )
    comps = comps_result.data or []

    valuation_result = (
        client.table("valuations")
        .select("*")
        .eq("item_id", item_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    valuation = valuation_result.data[0] if valuation_result.data else None

    listing_result = (
        client.table("generated_listings")
        .select("*")
        .eq("item_id", item_id)
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    listing = listing_result.data[0] if listing_result.data else None

    pub_result = (
        client.table("listing_publications")
        .select("*")
        .eq("item_id", item_id)
        .order("created_at", desc=False)
        .execute()
    )
    publications = pub_result.data or []

    return {
        "item": item,
        "comps": comps,
        "valuation": valuation,
        "listing": listing,
        "publications": publications,
    }
