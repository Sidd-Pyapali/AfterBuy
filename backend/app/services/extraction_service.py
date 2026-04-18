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


class ItemExtraction(BaseModel):
    brand: str | None = None
    item_type: str | None = None
    category: str | None = None
    likely_product_name: str | None = None
    color: str | None = None
    visible_condition: str | None = None
    notable_details: list[str] = []
    confidence: float = 0.5


_SYSTEM_PROMPT = """You are an expert at identifying secondhand and resale items from photos.

Analyze the image and extract structured information to help the owner list it for resale.

Rules:
- Set brand to null if you cannot clearly identify it from visual cues alone
- Do not invent model numbers, sizes, or materials you cannot clearly see in the image
- visible_condition must be one of: "new", "like_new", "good", "fair", "poor"
- confidence is a float from 0.0 to 1.0 reflecting overall identification certainty
- notable_details should list 2 to 5 observable features relevant to resale (e.g. "quilted exterior", "gold hardware", "scuff on right toe")
- If the image is blurry, ambiguous, or hard to identify, lower confidence accordingly"""


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
        max_tokens=512,
    )

    choice = response.choices[0].message
    if choice.refusal:
        raise RuntimeError(f"OpenAI refused the request: {choice.refusal}")
    if choice.parsed is None:
        raise RuntimeError("OpenAI returned no parsed extraction result")

    return choice.parsed.model_dump()
