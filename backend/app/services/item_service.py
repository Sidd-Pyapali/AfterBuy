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
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )
    publication = pub_result.data[0] if pub_result.data else None

    return {
        "item": item,
        "comps": comps,
        "valuation": valuation,
        "listing": listing,
        "publication": publication,
    }
