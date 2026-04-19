import uuid

_SUPPORTED_PLATFORMS = {"ebay", "poshmark", "depop", "facebook_marketplace"}

_PLATFORM_LABELS = {
    "ebay": "eBay",
    "poshmark": "Poshmark",
    "depop": "Depop",
    "facebook_marketplace": "Facebook Marketplace",
}


def mock_publish(platforms: list[str]) -> list[dict]:
    """Return mock publication records for the requested platforms.

    Only processes platforms in the supported set. Generates a fake listing ID
    to simulate what a real marketplace response might include.
    """
    results = []
    for platform in platforms:
        p = platform.lower().strip()
        if p not in _SUPPORTED_PLATFORMS:
            continue
        mock_id = f"MOCK-{uuid.uuid4().hex[:8].upper()}"
        results.append({
            "platform": p,
            "publication_status": "mock_published",
            "external_listing_id": mock_id,
            "external_listing_url": None,
            "raw_response_json": {
                "mock": True,
                "demo": True,
                "platform": p,
                "label": _PLATFORM_LABELS.get(p, p),
            },
        })
    return results
