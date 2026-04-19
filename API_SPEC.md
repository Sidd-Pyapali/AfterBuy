# AfterBuy API Specification

## 1. Purpose

This document defines the API contract for the AfterBuy MVP.

The goal of the API is to support one clean end-to-end user flow:

1. Upload item image
2. Extract item metadata
3. Fetch comparable listings
4. Compute valuation
5. Generate marketplace-ready listing
6. Optionally publish to a supported marketplace
7. Retrieve full assembled item state for rendering

This API spec is written for implementation clarity, frontend-backend coordination, and Claude Code guidance.

It is intentionally narrow.  
It is not a generalized platform API.  
It is not designed for broad third-party integrations.  
It exists to support the AfterBuy hackathon MVP.

---

## 2. Global API Principles

### 2.1 API Style
- REST-style JSON API
- multipart upload for image ingestion
- predictable response shapes
- minimal nesting beyond what is necessary
- explicit success/failure semantics

### 2.2 Backend Base URL
During local development, assume:

`http://localhost:8000`

Frontend should consume this from environment configuration, not hardcode it.

### 2.3 Response Format Philosophy
Responses should be:
- structured
- stable
- easy for the frontend to consume
- explicit about uncertainty
- explicit about errors

Avoid highly variable or loosely typed responses.

### 2.4 Error Format
All non-2xx responses should return JSON in a consistent shape:

```json
{
  "error": {
    "code": "SOME_ERROR_CODE",
    "message": "Human-readable error message",
    "details": {}
  }
}
```

### Error format rules
- `code` should be short and machine-friendly
- `message` should be human-readable
- `details` can be omitted or empty if not needed
- never leak secrets or raw tokens in errors

## 2.5 Timestamps

All timestamps should be ISO 8601 strings in UTC when returned from the API.

## 2.6 IDs

Use string IDs consistently in the JSON API even if the database uses UUIDs or internal IDs.

## 3. Resource Model Overview

The main resources in the API are:

- `item`
- `market_comp`
- `valuation`
- `generated_listing`
- `listing_publication`

The frontend mainly cares about:

- creating an item from an upload
- viewing an assembled item result

## 4. Endpoint Summary

### Required Endpoints
- `GET /`
- `POST /extract-item`
- `POST /find-comps`
- `POST /valuate-item`
- `POST /generate-listing`
- `GET /item/{item_id}`

### Optional Endpoints
- `POST /process-item`
- `POST /publish/marketplace`
- `GET /items`
- `GET /health`

## 5. Health and Status Endpoints

### 5.1 `GET /`

#### Purpose
Basic backend health check.

#### Request
No body.

#### Response
```json
{
  "message": "AfterBuy backend is running"
}
```

#### Notes
This route should be extremely simple and reliable.

### 5.2 `GET /health` (optional but recommended)

#### Purpose

More structured health check for service status.

#### Request

No body.

#### Response

```json
{
  "status": "ok",
  "services": {
    "api": "ok",
    "supabase": "unknown",
    "openai": "unknown",
    "market_data_provider": "unknown"
  }
}
```

#### Notes

This can remain lightweight.  
Do not block on complex dependency checks for MVP.

## 6. Item Extraction Flow

### 6.1 `POST /extract-item`

#### Purpose

Accept an uploaded item image, store it, run image extraction, and create an item record.

#### Content Type

`multipart/form-data`

#### Request Fields

- `file`: required image file
- `input_text`: optional free-text hint from user
- `source_type`: optional string, default `photo`

#### Example Request

Form-data:

- `file`: `jacket.jpg`
- `input_text`: `"black north face puffer"`
- `source_type`: `"photo"`

#### Success Response

```json
{
  "item": {
    "id": "item_123",
    "created_at": "2026-04-18T17:00:00Z",
    "image_url": "https://example.com/item-images/abc.jpg",
    "source_type": "photo",
    "input_text": "black north face puffer",
    "brand": "The North Face",
    "category": "outerwear",
    "item_type": "puffer jacket",
    "title_guess": "The North Face black puffer jacket",
    "color": "black",
    "condition": "good",
    "confidence_score": 0.82,
    "extracted_metadata": {
      "brand": "The North Face",
      "item_type": "puffer jacket",
      "category": "outerwear",
      "likely_product_name": "The North Face black puffer jacket",
      "color": "black",
      "visible_condition": "good",
      "notable_details": [
        "quilted pattern",
        "zip front"
      ],
      "confidence": 0.82
    }
  },
  "processing": {
    "step": "extraction_complete",
    "next_recommended_action": "find_comps"
  }
}
```

#### Failure Responses

##### Invalid file

```json
{
  "error": {
    "code": "INVALID_FILE_TYPE",
    "message": "Uploaded file must be a supported image format.",
    "details": {}
  }
}
```

##### Missing file

```json
{
  "error": {
    "code": "MISSING_FILE",
    "message": "No image file was provided.",
    "details": {}
  }
}
```

##### Storage failure

```json
{
  "error": {
    "code": "IMAGE_UPLOAD_FAILED",
    "message": "Unable to store uploaded image.",
    "details": {}
  }
}
```

##### Extraction failure

```json
{
  "error": {
    "code": "EXTRACTION_FAILED",
    "message": "Unable to extract item details from image.",
    "details": {}
  }
}
```

#### Implementation Notes

- This endpoint should persist the item record immediately
- Extraction output must be structured and grounded
- If extraction is partially uncertain, still return best-effort fields with lower confidence
- Do not fail just because brand is unknown

## 7. Market Comparable Search

### 7.1 `POST /find-comps`

#### Purpose

Search a market data provider for comparable listings using extracted item metadata.

#### Request Body

```json
{
  "item_id": "item_123"
}
```

#### Alternate Request Body

If needed, support direct metadata payload:

```json
{
  "brand": "The North Face",
  "category": "outerwear",
  "item_type": "puffer jacket",
  "title_guess": "The North Face black puffer jacket",
  "color": "black"
}
```

#### Preferred MVP Contract

Use `item_id` and let backend load metadata from DB.

#### Success Response

```json
{
  "item_id": "item_123",
  "search_strategy": {
    "primary_query": "The North Face black puffer jacket",
    "fallback_query": "The North Face outerwear puffer jacket",
    "source": "serpapi"
  },
  "comps": [
    {
      "id": "comp_1",
      "source": "serpapi",
      "title": "The North Face black puffer jacket mens medium",
      "price": 89.99,
      "currency": "USD",
      "url": "https://example.com/products/comp1",
      "image_url": "https://example.com/comp1.jpg",
      "condition": "Pre-owned",
      "similarity_score": 0.91
    },
    {
      "id": "comp_2",
      "source": "serpapi",
      "title": "North Face black quilted jacket",
      "price": 74.00,
      "currency": "USD",
      "url": "https://example.com/products/comp2",
      "image_url": "https://example.com/comp2.jpg",
      "condition": "Used",
      "similarity_score": 0.78
    }
  ],
  "comp_count": 2
}
```

#### Failure Responses

##### Item not found

```json
{
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "No item was found for the given item_id.",
    "details": {}
  }
}
```

##### Market data provider failure

```json
{
  "error": {
    "code": "MARKETPLACE_FETCH_FAILED",
    "message": "Unable to retrieve comparable listings at this time.",
    "details": {
      "source": "serpapi"
    }
  }
}
```

#### No Results Response

This should not be treated as an error if the item exists but no comps are found.

```json
{
  "item_id": "item_123",
  "search_strategy": {
    "primary_query": "The North Face black puffer jacket",
    "fallback_query": "The North Face outerwear puffer jacket",
    "source": "serpapi"
  },
  "comps": [],
  "comp_count": 0,
  "warnings": [
    "No strong comparable listings were found."
  ]
}
```

#### Implementation Notes

- Persist normalized comps to DB
- Keep raw result JSON internally if needed for debugging
- Do not return raw provider payload directly to frontend
- Similarity score can be heuristic and backend-generated

## 8. Valuation Endpoint

### 8.1 `POST /valuate-item`

#### Purpose

Compute a valuation range and suggested listing price using comps and extracted item metadata.

#### Request Body

```json
{
  "item_id": "item_123"
}
```

#### Success Response

```json
{
  "item_id": "item_123",
  "valuation": {
    "id": "valuation_123",
    "estimated_low": 68.0,
    "estimated_mid": 82.0,
    "estimated_high": 95.0,
    "suggested_listing_price": 84.0,
    "confidence": "medium",
    "valuation_reason": "Based on 5 comparable market listings with moderate title and brand similarity.",
    "valuation_method": "comp_weighted_heuristic",
    "comp_count": 5
  }
}
```

#### Failure Responses

##### Missing comps and no fallback

```json
{
  "error": {
    "code": "VALUATION_FAILED",
    "message": "Unable to generate a reliable valuation for this item.",
    "details": {}
  }
}
```

##### Item not found

```json
{
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "No item was found for the given item_id.",
    "details": {}
  }
}
```

#### Low-Confidence Example Response

```json
{
  "item_id": "item_123",
  "valuation": {
    "id": "valuation_123",
    "estimated_low": 45.0,
    "estimated_mid": 60.0,
    "estimated_high": 80.0,
    "suggested_listing_price": 62.0,
    "confidence": "low",
    "valuation_reason": "Limited exact matches were found, so this estimate uses broader comparable items.",
    "valuation_method": "fallback_heuristic",
    "comp_count": 2
  }
}
```

#### Implementation Notes

- The frontend should rely on the `confidence` and `valuation_reason` fields
- Do not hide uncertainty
- Suggested listing price should be realistic relative to the range

## 9. Listing Generation Endpoint

### 9.1 `POST /generate-listing`

#### Purpose

Generate a marketplace-ready title and description using extracted metadata and valuation.

#### Request Body

```json
{
  "item_id": "item_123",
  "platform": "generic"
}
```

#### Supported Platforms for MVP

- `generic`
- `marketplace`

Platform-specific generation can be shallow at first.  
Do not overfit listing copy to many marketplace differences for the MVP.

#### Success Response

```json
{
  "item_id": "item_123",
  "listing": {
    "id": "listing_123",
    "platform": "generic",
    "title": "The North Face Black Puffer Jacket - Pre-Owned",
    "description": "Pre-owned black The North Face puffer jacket in good condition. Quilted design with zip front. Great everyday outerwear piece with visible signs of normal wear.",
    "condition_note": "Good pre-owned condition with normal visible wear.",
    "suggested_price": 84.0,
    "attributes": {
      "brand": "The North Face",
      "category": "outerwear",
      "color": "black",
      "condition": "good"
    }
  }
}
```

#### Failure Responses

##### Missing valuation

```json
{
  "error": {
    "code": "MISSING_VALUATION",
    "message": "A valuation must exist before generating a listing.",
    "details": {}
  }
}
```

##### Generation failure

```json
{
  "error": {
    "code": "LISTING_GENERATION_FAILED",
    "message": "Unable to generate listing content at this time.",
    "details": {}
  }
}
```

## 9.2 `PATCH /listing/{item_id}`

### Purpose
Update the generated listing content after user review/edit.

### Request Body

```json
{
  "title": "The North Face Green Jacket",
  "description": "Pre-owned green jacket in good condition...",
  "condition_note": "Light wear with no major flaws.",
  "suggested_price": 141.0
}
```

#### Success Response
```json
{
  "item_id": "item_123",
  "listing": {
    "id": "listing_123",
    "platform": "generic",
    "title": "The North Face Green Jacket",
    "description": "Pre-owned green jacket in good condition...",
    "condition_note": "Light wear with no major flaws.",
    "suggested_price": 141.0,
    "attributes": {
      "brand": "The North Face",
      "category": "Clothing",
      "color": "Green",
      "condition": "like_new"
    }
  }
}
```
#### Notes
- this supports a review/edit before publish flow
- only editable listing fields should be updated

## 10. Full Assembled Item Endpoint

### 10.1 `GET /item/{item_id}`

#### Purpose

Return all relevant data needed to render the final item result page.

#### Path Parameters

- `item_id`: required

#### Success Response

```json
{
  "item": {
    "id": "item_123",
    "created_at": "2026-04-18T17:00:00Z",
    "image_url": "https://example.com/item-images/abc.jpg",
    "source_type": "photo",
    "input_text": "black north face puffer",
    "brand": "The North Face",
    "category": "outerwear",
    "item_type": "puffer jacket",
    "title_guess": "The North Face black puffer jacket",
    "color": "black",
    "condition": "good",
    "confidence_score": 0.82,
    "extracted_metadata": {
      "brand": "The North Face",
      "item_type": "puffer jacket",
      "category": "outerwear",
      "likely_product_name": "The North Face black puffer jacket",
      "color": "black",
      "visible_condition": "good",
      "notable_details": [
        "quilted pattern",
        "zip front"
      ],
      "confidence": 0.82
    }
  },
  "comps": [
    {
      "id": "comp_1",
      "source": "serpapi",
      "title": "The North Face black puffer jacket mens medium",
      "price": 89.99,
      "currency": "USD",
      "url": "https://example.com/products/comp1",
      "image_url": "https://example.com/comp1.jpg",
      "condition": "Pre-owned",
      "similarity_score": 0.91
    }
  ],
  "valuation": {
    "id": "valuation_123",
    "estimated_low": 68.0,
    "estimated_mid": 82.0,
    "estimated_high": 95.0,
    "suggested_listing_price": 84.0,
    "confidence": "medium",
    "valuation_reason": "Based on 5 comparable market listings with moderate title and brand similarity.",
    "valuation_method": "comp_weighted_heuristic",
    "comp_count": 5
  },
  "listing": {
    "id": "listing_123",
    "platform": "generic",
    "title": "The North Face Black Puffer Jacket - Pre-Owned",
    "description": "Pre-owned black The North Face puffer jacket in good condition. Quilted design with zip front. Great everyday outerwear piece with visible signs of normal wear.",
    "condition_note": "Good pre-owned condition with normal visible wear.",
    "suggested_price": 84.0,
    "attributes": {
      "brand": "The North Face",
      "category": "outerwear",
      "color": "black",
      "condition": "good"
    }
  },
  "publication": null
}
```

#### Failure Response

```json
{
  "error": {
    "code": "ITEM_NOT_FOUND",
    "message": "No item was found for the given item_id.",
    "details": {}
  }
}
```

#### Implementation Notes

- This is the main frontend result page endpoint
- It should be stable and easy to consume
- Missing sub-resources should be returned as `null` or empty arrays, not as fatal errors, if the item exists

## 11. Orchestration Endpoint (Optional but Recommended)

### 11.1 `POST /process-item`

#### Purpose

Provide a single orchestration endpoint that performs:

- image upload and extraction
- comp retrieval
- valuation
- listing generation

This is optional.  
It may simplify the frontend and improve the demo flow.

#### Content Type

`multipart/form-data`

#### Request Fields

- `file`: required image file
- `input_text`: optional
- `source_type`: optional

#### Success Response

Same shape as `GET /item/{item_id}` with full assembled output:

```json
{
  "item": {},
  "comps": [],
  "valuation": {},
  "listing": {},
  "publication": null
}
```

#### Failure Response

Use standard error format.

#### Implementation Notes

- This is useful for a single-click demo flow
- If implemented, it should internally call the same service layers as the individual endpoints
- Do not duplicate business logic

## 12. Marketplace Publish and Inventory Endpoints (Optional Stretch)

### 12.1 `POST /publish/marketplace`

#### Purpose

Create a clearly labeled mock multi-market publish result for a generated listing and persist platform publication state.

#### Request Body

```json
{
  "item_id": "item_123",
  "platforms": ["ebay", "poshmark", "depop"]
}
```

#### Success Response

```json
{
  "item_id": "item_123",
  "publications": [
    {
      "id": "pub_123",
      "platform": "ebay",
      "publication_status": "mock_published",
      "external_listing_id": "ebay_demo_123",
      "external_listing_url": "https://example.com/demo/ebay/123"
    },
    {
      "id": "pub_124",
      "platform": "poshmark",
      "publication_status": "mock_published",
      "external_listing_id": "poshmark_demo_456",
      "external_listing_url": "https://example.com/demo/poshmark/456"
    }
  ],
  "warnings": [
    "This is a mock publish flow for demo purposes."
  ]
}
```

#### Failure Response

```json
{
  "error": {
    "code": "PUBLISH_FAILED",
    "message": "Unable to publish this listing to the selected marketplace.",
    "details": {}
  }
}
```

#### Implementation Notes

- this endpoint is optional
- for the hackathon MVP, a clearly labeled mock flow is preferred over a fragile real integration
- selected platforms should be persisted in publication records
- never pretend a real publish happened if it did not

### 12.2 `GET /items`

#### Purpose

Return a simple inventory list of uploaded items for dashboard and listing tracking views.

#### Query Parameters

Optional:

- `limit`
- `offset`

#### Success Response

```json
{
  "items": [
    {
      "id": "item_123",
      "image_url": "https://example.com/item-images/abc.jpg",
      "title_guess": "The North Face black puffer jacket",
      "category": "outerwear",
      "valuation_mid": 82.0,
      "listing_status": "mock_published",
      "platforms": ["ebay", "depop"],
      "created_at": "2026-04-18T17:00:00Z"
    }
  ],
  "pagination": {
    "limit": 20,
    "offset": 0,
    "total": 1
  }
}
```

#### Notes

- this is stretch only
- do not build before the core result flow is stable
- the inventory response should support lightweight tracking, not a complex admin dashboard

## 13. Backend Internal Service Boundaries

The API should be implemented using service boundaries like:

### `extraction_service`

Responsibilities:

- image analysis using OpenAI
- structured metadata extraction

### `storage_service`

Responsibilities:

- Supabase Storage upload
- image URL handling

### `item_service`

Responsibilities:

- item persistence
- reading/writing assembled item state

### `market_data_service`

Responsibilities:
- provider request construction
- market comparable retrieval
- result normalization
- provider-specific error handling

### `valuation_service`

Responsibilities:

- comp scoring
- outlier filtering
- valuation computation
- confidence determination

### `listing_service`

Responsibilities:

- prompt construction
- listing generation
- output validation

### `publication_service`

Responsibilities:

- optional marketplace publish flow
- publication persistence

These boundaries are not directly exposed to the frontend, but they should shape implementation.

## 14. Frontend Consumption Model

The frontend should prefer one of two modes:

### Mode A: Orchestrated Mode

Use `POST /process-item` for the whole flow.  
This is simpler for the final demo.

### Mode B: Stepwise Mode

Call:

1. `/extract-item`
2. `/find-comps`
3. `/valuate-item`
4. `/generate-listing`
5. `/item/{id}`

This may be easier to debug during development.

### Recommendation

Support stepwise logic internally if useful, but expose a smooth orchestrated flow for demo if possible.

## 15. Validation Rules

### Input Validation

- image file required for extraction
- reject unsupported file types
- enforce reasonable file size limits
- `item_id` required for dependent endpoints unless alternate payload supported

### Output Validation

- extraction payload must be structured
- valuation must satisfy:
  - `estimated_low <= estimated_mid <= estimated_high`
- listing generation must return non-empty title and description
- publication responses must clearly distinguish real vs mock

## 16. Security and Secret Handling

### Rules

- frontend must never receive secret keys
- OpenAI key remains backend-only
- market data provider and marketplace credentials remain backend-only
- Supabase service key remains backend-only
- only safe public config goes to frontend env

### Response Safety

- do not return raw marketplace auth payloads
- do not return raw OpenAI response blobs to frontend
- avoid exposing internal debugging data in normal responses

## 17. Logging and Debugging Guidance

For implementation:

- log backend processing steps clearly
- log external API failures in a developer-friendly way
- avoid logging secrets
- avoid logging full raw image data

Useful log checkpoints:

- image received
- image uploaded
- extraction complete
- comps fetched
- valuation generated
- listing generated
- publish attempted

## 18. API Versioning

No formal versioning is required for the hackathon MVP.

Do not introduce `/v1` unless it is already convenient.  
Keep the API surface simple.

## 19. Final API Contract Priorities

If time is limited, prioritize the following endpoints in this order:

1. `GET /`
2. `POST /extract-item`
3. `POST /find-comps`
4. `POST /valuate-item`
5. `POST /generate-listing`
6. `GET /item/{item_id}`
7. `POST /process-item`
8. `POST /publish/marketplace`
9. `GET /items`

The app is viable without the last three.  
The app is not viable without the first six.

## 20. Final Principle

The API should optimize for:

- clarity
- predictable response shapes
- robust golden path behavior
- honest uncertainty
- easy frontend integration

Not:

- excessive generality
- over-designed platform semantics
- unnecessary flexibility
