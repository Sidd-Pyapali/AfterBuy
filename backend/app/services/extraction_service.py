import base64
from pydantic import BaseModel
from openai import OpenAI
from app.core import config

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        config.require_openai()
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
    return _client


class WearSignal(BaseModel):
    zone: str
    signal: str
    severity: str
    confidence: float


class WearAssessment(BaseModel):
    wear_level: str
    wear_confidence: float
    wear_summary: str
    pricing_adjustment_factor: float
    wear_signals: list[WearSignal]


class ItemExtraction(BaseModel):
    brand: str | None = None
    item_type: str | None = None
    category: str | None = None
    likely_product_name: str | None = None
    color: str | None = None
    visible_condition: str | None = None
    notable_details: list[str] = []
    confidence: float = 0.5
    wear_assessment: WearAssessment | None = None


_SYSTEM_PROMPT = """You are an expert at identifying secondhand wardrobe and resale items from photos.

Analyze the image and extract structured item details for resale purposes.

## Item identification rules
- Set brand to null if you cannot clearly identify it from visual cues alone
- Do not invent model numbers, sizes, or materials you cannot clearly see in the image
- visible_condition must be one of: "new", "like_new", "good", "fair", "poor"
- confidence is a float from 0.0 to 1.0 reflecting overall identification certainty
- notable_details should list 2 to 5 observable features relevant to resale (e.g. "quilted exterior", "gold hardware", "scuff on right toe")

## Handling low-quality or ambiguous images
- If the image is blank, nearly blank, very dark, or contains no physical item, set confidence to 0.1 or lower and return null for all metadata fields
- If the image is so blurry or obscured that no item can be identified, set confidence to 0.1 or lower and return null for all metadata fields
- Do not guess or infer an item type from context alone — require clear visual evidence of the item itself
- Never fabricate a brand, product name, or category when the image does not clearly show one

## Wear assessment rules
Always return a wear_assessment object. Use conservative, image-grounded values.

wear_level values: "none", "light", "moderate", "heavy", "unknown"
- "none": item appears new or like-new with no visible wear
- "light": minor visible wear — slight pilling, faint creasing, barely visible scuffs
- "moderate": clearly visible wear — pilling, fading, noticeable scuffs or abrasion
- "heavy": significant wear — prominent fading, tearing, or structural damage visible
- "unknown": image quality too low, relevant areas not visible, or item is not wardrobe-relevant

wear_confidence: 0.0 to 1.0
- Lower when the image is blurry, distant, poorly lit, or shows limited garment coverage
- Lower when the relevant wear zones cannot be seen
- Use 0.1 for non-wardrobe items or fully unidentifiable images

pricing_adjustment_factor: 0.5 to 1.0 (how much to adjust price for visible wear)
- "none": 1.0
- "light": 0.90 to 0.95
- "moderate": 0.75 to 0.85
- "heavy": 0.50 to 0.70
- "unknown": 1.0 (never penalize uncertain wear)

Wear zones to inspect by item type:
- Outerwear (jackets, coats): cuffs, collar, hem, zipper area, elbows, shoulders, pockets
- Tops (shirts, hoodies, sweaters): collar, cuffs, elbows, fabric body
- Pants/bottoms: knees, waistband, hem, seat area
- Shoes/footwear: toe box, heel, sole, upper surface, insole
- Bags (backpacks, purses, totes): corners, straps, handles, hardware, bottom, zipper area
- Accessories: surface finish, edges, clasp or closure mechanism

Each wear_signal must include:
- zone: specific area of the item (e.g. "cuffs", "collar", "toe box", "corner")
- signal: the wear type observed (e.g. "fraying", "pilling", "fading", "scuff", "stain", "abrasion")
- severity: "light", "moderate", or "heavy"
- confidence: 0.0 to 1.0 (how confident you are this signal is visible in the image)

Critical: Only report wear signals that are clearly visible in the provided photo.
Do not infer hidden damage, odor, wash history, softness loss, or invisible structural issues.
If no wear is visible, return an empty wear_signals list with wear_level "none"."""


def extract_item(image_bytes: bytes, content_type: str, input_text: str | None = None) -> dict:
    client = _get_client()

    b64 = base64.b64encode(image_bytes).decode("utf-8")
    data_url = f"data:{content_type};base64,{b64}"

    user_content: list = []
    if input_text:
        user_content.append({
            "type": "text",
            "text": f"The user describes this item as: {input_text}\n\nAnalyze the image and extract structured item details.",
        })
    user_content.append({
        "type": "image_url",
        "image_url": {"url": data_url, "detail": "high"},
    })

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": user_content},
        ],
        response_format=ItemExtraction,
        max_tokens=800,
    )

    choice = response.choices[0].message
    if choice.refusal:
        raise RuntimeError(f"OpenAI refused the request: {choice.refusal}")
    if choice.parsed is None:
        raise RuntimeError("OpenAI returned no parsed extraction result")

    result = choice.parsed.model_dump()
    # Rename wear_assessment key to match API spec nesting
    if result.get("wear_assessment") is not None:
        result["wear_assessment"] = result["wear_assessment"]
    return result
