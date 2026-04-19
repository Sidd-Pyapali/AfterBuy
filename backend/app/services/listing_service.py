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


class ListingOutput(BaseModel):
    title: str
    description: str
    condition_note: str


_SYSTEM_PROMPT = """You are an expert at writing secondhand marketplace listings.

Write clean, factual, resale-ready listing content based only on the provided item details.

Rules:
- Title: under 80 characters, Title Case, suitable for eBay / Poshmark / Depop
- Description: 2 to 4 sentences, factual, neutral tone
- Condition note: 1 sentence honestly describing the item's condition
- Do NOT invent measurements, exact materials, model numbers, or authenticity details
- Do NOT use hype language ("rare", "must-see", "amazing deal")
- Do NOT include a price in the title or description
- Do NOT fabricate collection names, seasons, or SKUs
- If metadata is sparse, write conservatively based only on what is provided
- Tone: clean and neutral, as if written by a careful human seller"""


def generate_listing(item: dict, valuation: dict | None) -> dict:
    client = _get_client()

    parts: list[str] = []
    for field, label in [
        ("brand", "Brand"),
        ("item_type", "Item type"),
        ("category", "Category"),
        ("title_guess", "Identified as"),
        ("color", "Color"),
        ("condition", "Condition"),
    ]:
        val = item.get(field)
        if val:
            parts.append(f"{label}: {val}")

    metadata = item.get("extracted_metadata_json") or {}
    notable = metadata.get("notable_details") or []
    if notable:
        parts.append(f"Notable details: {', '.join(notable)}")

    if valuation:
        price = valuation.get("suggested_listing_price")
        if price:
            parts.append(f"Suggested listing price: ${price:.0f}")

    item_context = "\n".join(parts) if parts else "Limited item information available."

    prompt = (
        "Generate a marketplace listing for the following item:\n\n"
        f"{item_context}\n\n"
        "Write factual, grounded copy based only on the details above."
    )

    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
        response_format=ListingOutput,
        max_tokens=512,
    )

    choice = response.choices[0].message
    if choice.refusal:
        raise RuntimeError(f"OpenAI refused the listing request: {choice.refusal}")
    if choice.parsed is None:
        raise RuntimeError("OpenAI returned no parsed listing result")

    result = choice.parsed.model_dump()
    result["platform"] = "generic"
    result["suggested_price"] = valuation.get("suggested_listing_price") if valuation else None
    result["attributes"] = {
        "brand": item.get("brand"),
        "category": item.get("category"),
        "color": item.get("color"),
        "condition": item.get("condition"),
    }
    return result
