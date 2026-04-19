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


_SYSTEM_PROMPT = """You are an expert at writing factual, resale-ready marketplace listings for platforms like eBay, Poshmark, and Facebook Marketplace.

## Title rules
- Under 80 characters, Title Case
- Pattern: Brand + Item Type + Color or Key Feature
  Good: "The North Face Full Zip Fleece Jacket Black", "Hydro Flask Standard Mouth Water Bottle"
  Bad: "Amazing jacket perfect for winter", "Rare vintage item must see"
- Do not include price, condition, or size in the title
- Do not invent model numbers, SKUs, collection names, or season names
- If brand is unknown, use descriptive words only

## Description rules
- 2 to 4 sentences
- Structure: brief factual overview → visible condition → note to see photos
- Neutral, honest tone — written as a careful human seller would
- No invented measurements, exact materials, or specifications not provided
- No hype language ("amazing", "rare", "incredible deal")
- Do not repeat the title verbatim
- If wear information is provided, weave it naturally into the description

## Condition note rules
- 1 to 2 sentences, honest and specific
- If visible wear signals are provided, reference the specific zones (e.g. "Shows light pilling at the cuffs and collar")
- If no wear signals are provided or wear is unknown, write a conservative general note based on the stated condition
- Do not overclaim ("pristine", "perfect") unless condition strongly supports it
- Do not fabricate wear that was not described — only describe what is provided
- Phrase wear as visible from photos (e.g. "visible in provided photos") rather than claiming hidden knowledge"""


# Category detection ──────────────────────────────────────────────────────────

_APPAREL_TOKENS = {
    "jacket", "coat", "hoodie", "hooded", "shirt", "pants", "dress", "sweater",
    "top", "blouse", "shorts", "skirt", "vest", "pullover", "tee", "cardigan",
    "blazer", "trench", "parka", "fleece", "windbreaker", "outerwear", "apparel",
    "clothing", "wear", "sweatshirt", "anorak", "shell", "raincoat",
}

_DRINKWARE_TOKENS = {
    "bottle", "tumbler", "flask", "mug", "cup", "thermos", "drinkware",
    "canteen", "jug", "hydro", "contigo", "yeti", "stanley",
}

_BAGS_TOKENS = {
    "bag", "backpack", "purse", "tote", "handbag", "wallet", "clutch",
    "satchel", "duffel", "crossbody", "messenger", "briefcase", "pouch",
}

_FOOTWEAR_TOKENS = {
    "shoe", "shoes", "boot", "boots", "sneaker", "sneakers", "sandal",
    "loafer", "heel", "heels", "footwear", "kicks",
}

_ELECTRONICS_TOKENS = {
    "phone", "laptop", "tablet", "camera", "iphone", "macbook", "ipad",
    "computer", "electronics", "headphone", "earbuds", "speaker",
    "console", "gaming", "keyboard", "mouse", "monitor",
}


def _detect_category_key(item: dict) -> str:
    tokens: set[str] = set()
    for field in ("category", "item_type", "title_guess"):
        val = (item.get(field) or "").lower()
        tokens.update(val.split())

    if tokens & _APPAREL_TOKENS:
        return "apparel"
    if tokens & _DRINKWARE_TOKENS:
        return "drinkware"
    if tokens & _BAGS_TOKENS:
        return "bags"
    if tokens & _FOOTWEAR_TOKENS:
        return "footwear"
    if tokens & _ELECTRONICS_TOKENS:
        return "electronics"
    return "general"


# Item specifics ──────────────────────────────────────────────────────────────

def _build_item_specifics(item: dict) -> dict:
    cat_key = _detect_category_key(item)
    metadata = item.get("extracted_metadata_json") or {}
    notable: list[str] = metadata.get("notable_details") or []
    notable_lower = [n.lower() for n in notable]

    base: dict[str, str | None] = {
        "Brand": item.get("brand"),
        "Category": item.get("category"),
        "Type": item.get("item_type"),
        "Color": item.get("color"),
        "Condition": item.get("condition"),
    }

    if cat_key == "drinkware":
        materials = ("stainless", "plastic", "aluminum", "ceramic", "glass", "titanium")
        for nl, n in zip(notable_lower, notable):
            if any(m in nl for m in materials):
                base["Material"] = n
                break

    elif cat_key == "apparel":
        closures = ("full zip", "half zip", "button", "snap", "velcro", "hook")
        for nl, n in zip(notable_lower, notable):
            if any(c in nl for c in closures):
                base["Closure"] = n
                break

    # Add visible wear level if meaningful
    wear = metadata.get("wear_assessment") or {}
    wear_level = (wear.get("wear_level") or "").lower()
    if wear_level in ("none", "light", "moderate", "heavy"):
        label_map = {"none": "No visible wear", "light": "Light wear", "moderate": "Moderate wear", "heavy": "Heavy wear"}
        base["Visible Wear"] = label_map[wear_level]

    return {k: v for k, v in base.items() if v and str(v).strip()}


# Photo checklist ─────────────────────────────────────────────────────────────

_PHOTO_CHECKLISTS: dict[str, list[str]] = {
    "apparel": [
        "Front view",
        "Back view",
        "Logo or branding close-up",
        "Tag or label",
        "Zipper or pocket detail",
        "Any wear or flaws",
    ],
    "drinkware": [
        "Front view",
        "Back view",
        "Lid or opening close-up",
        "Branding close-up",
        "Bottom or base",
        "Any dents, scratches, or wear",
    ],
    "bags": [
        "Front view",
        "Back view",
        "Interior",
        "Strap or handle close-up",
        "Hardware close-up",
        "Corner wear or flaws",
    ],
    "footwear": [
        "Side profile (both shoes)",
        "Top-down view",
        "Sole",
        "Toe box",
        "Heel",
        "Brand label or tag",
        "Any wear or flaws",
    ],
    "electronics": [
        "Front view",
        "Back view",
        "Ports and buttons",
        "Screen or display",
        "Branding close-up",
        "Any damage or wear",
    ],
    "general": [
        "Front view",
        "Back view",
        "Branding close-up",
        "Any wear or flaws",
    ],
}


def _build_photo_checklist(category_key: str) -> list[str]:
    return _PHOTO_CHECKLISTS.get(category_key, _PHOTO_CHECKLISTS["general"])


# Context builder ─────────────────────────────────────────────────────────────

def _build_listing_context(item: dict, valuation: dict | None) -> str:
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

    # Include visible wear context when meaningful
    wear = metadata.get("wear_assessment") or {}
    wear_level = (wear.get("wear_level") or "unknown").lower()
    wear_confidence = float(wear.get("wear_confidence") or 0)
    wear_summary = wear.get("wear_summary") or ""
    wear_signals: list[dict] = wear.get("wear_signals") or []

    if wear_level not in ("unknown",) and wear_confidence >= 0.35:
        parts.append(f"Visible wear level: {wear_level}")
        if wear_summary:
            parts.append(f"Wear summary: {wear_summary}")
        if wear_signals:
            signal_lines = []
            for s in wear_signals[:4]:  # cap at 4 signals to keep prompt tight
                zone = s.get("zone", "")
                signal = s.get("signal", "")
                severity = s.get("severity", "")
                sig_confidence = float(s.get("confidence") or 0)
                if zone and signal and sig_confidence >= 0.40:
                    signal_lines.append(f"{zone}: {severity} {signal}")
            if signal_lines:
                parts.append(f"Visible wear signals: {', '.join(signal_lines)}")
    elif wear_level == "none" and wear_confidence >= 0.5:
        parts.append("Visible wear: none visible in photos")

    if valuation:
        price = valuation.get("suggested_listing_price")
        if price:
            parts.append(f"Suggested listing price: ${price:.0f}")

    return "\n".join(parts) if parts else "Limited item information available."


# Main entry point ────────────────────────────────────────────────────────────

def generate_listing(item: dict, valuation: dict | None) -> dict:
    client = _get_client()

    item_context = _build_listing_context(item, valuation)
    cat_key = _detect_category_key(item)

    prompt = (
        "Generate a marketplace listing for the following item:\n\n"
        f"{item_context}\n\n"
        "Write factual, grounded copy based only on the details above. "
        "If wear signals are provided, reference them honestly in the condition note."
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
    result["item_specifics"] = _build_item_specifics(item)
    result["photo_checklist"] = _build_photo_checklist(cat_key)
    return result
