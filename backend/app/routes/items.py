from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from app.services import storage_service, item_service, extraction_service, market_data_service, valuation_service, listing_service, publication_service

router = APIRouter()

ALLOWED_CONTENT_TYPES = {"image/jpeg", "image/png", "image/webp"}
MAX_FILE_SIZE = 15 * 1024 * 1024  # 15MB


def _error(code: str, message: str, status: int = 400) -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={"error": {"code": code, "message": message, "details": {}}},
    )


def _serialize_item(db_item: dict) -> dict:
    return {
        "id": db_item["id"],
        "created_at": db_item["created_at"],
        "image_url": db_item["image_url"],
        "source_type": db_item["source_type"],
        "input_text": db_item["input_text"],
        "brand": db_item["brand"],
        "category": db_item["category"],
        "item_type": db_item["item_type"],
        "title_guess": db_item["title_guess"],
        "color": db_item["color"],
        "condition": db_item["condition"],
        "confidence_score": db_item["confidence_score"],
        "extracted_metadata": db_item.get("extracted_metadata_json"),
    }


@router.post("/extract-item")
def extract_item_endpoint(
    file: UploadFile = File(...),
    input_text: str | None = Form(None),
    source_type: str = Form("photo"),
):
    if not file.content_type or file.content_type not in ALLOWED_CONTENT_TYPES:
        return _error("INVALID_FILE_TYPE", "Uploaded file must be a JPEG, PNG, or WebP image.")

    file_bytes = file.file.read()

    if not file_bytes:
        return _error("MISSING_FILE", "No image file was provided.")

    if len(file_bytes) > MAX_FILE_SIZE:
        return _error("FILE_TOO_LARGE", "Image must be under 15MB.")

    try:
        image_url = storage_service.upload_image(
            file_bytes,
            file.filename or "image.jpg",
            file.content_type,
        )
    except Exception as exc:
        print(f"[extract-item] Storage upload failed: {exc}")
        return _error("IMAGE_UPLOAD_FAILED", "Unable to store uploaded image.", 500)

    item = item_service.create_item(image_url, source_type, input_text)

    try:
        extraction = extraction_service.extract_item(file_bytes, file.content_type, input_text)
    except Exception as exc:
        print(f"[extract-item] Extraction failed: {exc}")
        return _error("EXTRACTION_FAILED", "Unable to extract item details from image.", 500)

    item = item_service.update_item_extraction(item["id"], extraction)

    return {
        "item": _serialize_item(item),
        "processing": {
            "step": "extraction_complete",
            "next_recommended_action": "find_comps",
        },
    }


class FindCompsRequest(BaseModel):
    item_id: str


# Minimum confidence to attempt a comparable search. Below this threshold,
# extraction results are too weak to produce meaningful queries.
_COMP_SEARCH_MIN_CONFIDENCE = 0.35


def _is_item_searchable(item: dict) -> bool:
    """Return True only if the item has enough metadata to search reliably."""
    confidence = item.get("confidence_score") or 0.0
    if confidence < _COMP_SEARCH_MIN_CONFIDENCE:
        return False
    has_title = bool((item.get("title_guess") or "").strip())
    has_brand_and_type = (
        bool((item.get("brand") or "").strip())
        and bool((item.get("item_type") or "").strip())
    )
    return has_title or has_brand_and_type


@router.post("/find-comps")
def find_comps_endpoint(body: FindCompsRequest):
    assembled = item_service.get_assembled_item(body.item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    item = assembled["item"]

    if not _is_item_searchable(item):
        return {
            "item_id": body.item_id,
            "search_strategy": {"source": "serpapi", "skipped": True, "primary_query": None, "fallback_query": None},
            "comps": [],
            "comp_count": 0,
            "warnings": ["Item could not be confidently identified. Comparable search was skipped."],
        }

    try:
        comps, search_strategy = market_data_service.search_comps(item)
    except Exception as exc:
        print(f"[find-comps] Market data fetch failed: {exc}")
        return _error(
            "MARKETPLACE_FETCH_FAILED",
            "Unable to retrieve comparable listings at this time.",
            500,
        )

    persisted = item_service.insert_comps(body.item_id, comps)

    serialized_comps = [_serialize_comp(c) for c in persisted]

    warnings = []
    if not serialized_comps:
        warnings.append("No strong comparable listings were found.")

    response: dict = {
        "item_id": body.item_id,
        "search_strategy": search_strategy,
        "comps": serialized_comps,
        "comp_count": len(serialized_comps),
    }
    if warnings:
        response["warnings"] = warnings

    return response


def _serialize_comp(db_comp: dict) -> dict:
    return {
        "id": db_comp["id"],
        "source": db_comp["source"],
        "title": db_comp["comp_title"],
        "price": db_comp["comp_price"],
        "currency": db_comp.get("currency", "USD"),
        "url": db_comp["comp_url"],
        "image_url": db_comp["comp_image_url"],
        "condition": db_comp["comp_condition"],
        "similarity_score": db_comp["similarity_score"],
    }


def _serialize_valuation(db_val: dict) -> dict:
    return {
        "id": db_val["id"],
        "estimated_low": db_val["estimated_low"],
        "estimated_mid": db_val["estimated_mid"],
        "estimated_high": db_val["estimated_high"],
        "suggested_listing_price": db_val["suggested_listing_price"],
        "confidence": db_val["confidence"],
        "valuation_reason": db_val["valuation_reason"],
        "valuation_method": db_val["valuation_method"],
        "comp_count": db_val["comp_count"],
    }


def _serialize_publication(db_pub: dict) -> dict:
    return {
        "id": db_pub["id"],
        "platform": db_pub["platform"],
        "publication_status": db_pub["publication_status"],
        "external_listing_id": db_pub.get("external_listing_id"),
        "external_listing_url": db_pub.get("external_listing_url"),
    }


def _serialize_listing(db_listing: dict) -> dict:
    return {
        "id": db_listing["id"],
        "platform": db_listing["platform"],
        "title": db_listing["title"],
        "description": db_listing["description"],
        "condition_note": db_listing["condition_note"],
        "suggested_price": db_listing["suggested_price"],
        "attributes": db_listing.get("attributes_json"),
    }


class ValuateItemRequest(BaseModel):
    item_id: str


@router.post("/valuate-item")
def valuate_item_endpoint(body: ValuateItemRequest):
    assembled = item_service.get_assembled_item(body.item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    item = assembled["item"]
    comps = assembled["comps"]

    if not comps:
        return _error(
            "VALUATION_FAILED",
            "No comparable listings available. Run /find-comps first.",
            400,
        )

    try:
        valuation_data = valuation_service.compute_valuation(item, comps)
    except ValueError as exc:
        return _error("VALUATION_FAILED", str(exc), 400)
    except Exception as exc:
        print(f"[valuate-item] Valuation computation failed: {exc}")
        return _error("VALUATION_FAILED", "Unable to generate a reliable valuation for this item.", 500)

    persisted = item_service.insert_valuation(body.item_id, valuation_data)

    return {
        "item_id": body.item_id,
        "valuation": _serialize_valuation(persisted),
    }


class GenerateListingRequest(BaseModel):
    item_id: str
    platform: str = "generic"


@router.post("/generate-listing")
def generate_listing_endpoint(body: GenerateListingRequest):
    assembled = item_service.get_assembled_item(body.item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    item = assembled["item"]
    valuation = assembled["valuation"]

    if not valuation:
        return _error("MISSING_VALUATION", "A valuation must exist before generating a listing.", 400)

    try:
        listing_data = listing_service.generate_listing(item, valuation)
    except Exception as exc:
        print(f"[generate-listing] Listing generation failed: {exc}")
        return _error("LISTING_GENERATION_FAILED", "Unable to generate listing content at this time.", 500)

    listing_data["platform"] = body.platform
    persisted = item_service.insert_generated_listing(body.item_id, listing_data)

    return {
        "item_id": body.item_id,
        "listing": _serialize_listing(persisted),
    }


class UpdateListingRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    condition_note: str | None = None
    suggested_price: float | None = None


@router.patch("/listing/{listing_id}")
def update_listing_endpoint(listing_id: str, body: UpdateListingRequest):
    update_data = body.model_dump(exclude_none=True)
    if not update_data:
        return _error("NO_FIELDS", "No fields provided to update.", 400)
    try:
        updated = item_service.update_listing(listing_id, update_data)
    except ValueError as exc:
        return _error("LISTING_NOT_FOUND", str(exc), 404)
    except Exception as exc:
        print(f"[update-listing] Update failed: {exc}")
        return _error("UPDATE_FAILED", "Unable to update listing.", 500)
    return {"listing": _serialize_listing(updated)}


class PublishRequest(BaseModel):
    item_id: str
    platforms: list[str]


@router.post("/publish/marketplace")
def publish_marketplace_endpoint(body: PublishRequest):
    assembled = item_service.get_assembled_item(body.item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    if not body.platforms:
        return _error("NO_PLATFORMS", "At least one platform must be selected.", 400)

    publications = publication_service.mock_publish(body.platforms)
    if not publications:
        return _error("INVALID_PLATFORMS", "No valid platforms were provided.", 400)

    persisted = item_service.insert_publications(body.item_id, publications)

    return {
        "item_id": body.item_id,
        "publications": [_serialize_publication(p) for p in persisted],
        "warnings": ["This is a demo publish. No real marketplace listings were created."],
    }


@router.get("/items")
def list_items(limit: int = 20, offset: int = 0):
    items = item_service.get_items_list(limit=limit, offset=offset)
    return {"items": items, "pagination": {"limit": limit, "offset": offset, "total": len(items)}}


@router.get("/item/{item_id}")
def get_item(item_id: str):
    assembled = item_service.get_assembled_item(item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    return {
        "item": _serialize_item(assembled["item"]),
        "comps": [_serialize_comp(c) for c in assembled["comps"]],
        "valuation": _serialize_valuation(assembled["valuation"]) if assembled["valuation"] else None,
        "listing": _serialize_listing(assembled["listing"]) if assembled["listing"] else None,
        "publications": [_serialize_publication(p) for p in assembled["publications"]],
    }
