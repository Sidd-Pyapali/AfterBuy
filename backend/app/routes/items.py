from fastapi import APIRouter, File, Form, UploadFile
from fastapi.responses import JSONResponse
from app.services import storage_service, item_service, extraction_service

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


@router.get("/item/{item_id}")
def get_item(item_id: str):
    assembled = item_service.get_assembled_item(item_id)
    if assembled is None:
        return _error("ITEM_NOT_FOUND", "No item was found for the given item_id.", 404)

    return {
        "item": _serialize_item(assembled["item"]),
        "comps": assembled["comps"],
        "valuation": assembled["valuation"],
        "listing": assembled["listing"],
        "publication": assembled["publication"],
    }
