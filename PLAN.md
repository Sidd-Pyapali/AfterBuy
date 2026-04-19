# AfterBuy Plan

## 1. Project Identity

### Project Name
AfterBuy

### One-Line Description
AfterBuy is a mobile-first AI wardrobe resale agent that helps users identify items they own, estimate visible wear from images, price items for resale using market comps and wear-aware adjustments, generate a marketplace-ready listing, review and edit it, and track resale actions in one place.

### Core Product Thesis
Most commerce products optimize the moment before checkout.
AfterBuy optimizes what happens after checkout.

The product is not a marketplace.
The product is not a full resale platform.
The product is not a seller CRM.

It is an intelligence and action layer that sits between ownership and resale.

### Hackathon Track
Autonomous Agents

### Why This Belongs in Autonomous Agents
The product is not just generating copy.
It maintains item state, gathers external data, reasons over it, and prepares a concrete action.
The core agentic behavior is:

1. ingest a wardrobe item the user already owns
2. identify the item from images
3. estimate visible wear from the provided photos
4. find market context
5. adjust resale value based on comps and visible wear
6. generate a marketplace-ready listing payload
7. optionally distribute that listing across selected channels

This is not a passive dashboard.
It is a guided post-purchase ownership agent.

---

## 2. Problem Statement

### User Problem
People own items that may still have resale value, but when they decide they no longer want them, the selling process is frustrating and manual.

The friction points include:
- not remembering what the item is called
- not knowing what the item is worth now
- not knowing what similar items are listed for
- not knowing how to write a good listing
- having to repeat similar work across marketplaces
- lacking one place to track resale preparation and publishing state

### Important Clarification
This product is not about buying things to flip for profit.
It is about helping ordinary people recover value from items they already own when they are done using them.

### Why This Matters
The opportunity is meaningful because:
- resale is growing
- ordinary users have unused items
- listing friction is real
- valuation uncertainty prevents action
- current shopping assistants generally stop before or at checkout, not after purchase

### Product Framing
Do not frame this as:
- a resale bot
- a flipping tool
- a generic closet tracker
- a marketplace clone

Frame this as:
- post-purchase intelligence
- AI for ownership lifecycle
- the missing layer between buying and selling
- one place to understand and act on owned item value

---

## 3. Product Goals

## Primary Goal
Deliver a polished mobile-first web app demo that proves the full flow:

photo upload → item extraction + visible wear assessment → market comparables → wear-aware resale valuation → generated listing → optional marketplace distribution

## Secondary Goals
- store uploaded items and generated outputs
- make the UI feel consumer-grade, not like an internal tool
- make the valuation feel credible and transparent
- show enough technical depth to score highly on implementation
- show enough novelty to stand out from recommendation/chatbot projects

## Non-Goals
This MVP is not trying to:
- become a complete marketplace operations platform
- support deep inbox or offer management across all resale marketplaces
- implement long-term automated revaluation jobs
- support every category of personal item perfectly
- replace marketplace-native seller dashboards
- build sophisticated user auth and account systems

## Additional Demo Goals
- let the user review and edit the generated listing before publish
- demonstrate a clearly labeled mock multi-market publish flow
- show lightweight listing tracking inside AfterBuy
- support phone capture as well as image upload
- make the UI feel closer to a premium consumer shopping product
- make the product feel wardrobe-native, not like a generic listing generator
- surface visible wear clearly and honestly in both pricing and listing output
- guide the user toward better resale photos for wardrobe items

---

## 4. MVP Definition

### MVP Must Deliver
A user can:
1. open the app on a mobile-sized viewport
2. upload or photograph a wardrobe item they already own
3. have the system identify the item using OpenAI
4. see extracted attributes such as category, brand, title guess, color, condition
5. see a visible wear assessment based on the provided photos
6. have the system fetch comparable listings from a market data provider
7. see a wear-aware valuation range and suggested listing price
8. generate a resale listing with title, description, condition note, and structured specifics
9. review and edit the generated listing before distribution
10. optionally distribute to selected marketplaces through a clearly labeled simulated flow if real publishing is not feasible
11. optionally view uploaded items and listing/distribution state in a lightweight inventory dashboard

### MVP Success Standard
The MVP is successful if one golden path works smoothly and convincingly from beginning to end.

That matters more than supporting many edge cases.

### Golden Demo Path
Preferred demo item types:
- jacket
- sneaker
- bag
- hoodie
- other visually recognizable wardrobe item with clearly visible condition details

Why:
- easier image recognition
- easier comparable search
- better visual demo
- more aligned with Phia

---

## 5. Product Scope Boundaries

## In Scope
- photo upload
- OpenAI image understanding
- structured metadata extraction
- Supabase image storage
- Supabase persistence
- market comparable search using a provider such as SerpApi
- basic valuation engine using comparables and heuristics
- listing generation with OpenAI
- mobile-first frontend
- optional marketplace publish flow
- optional internal listing status view

## Explicitly Out of Scope for First Pass
- authentication
- user profiles
- multi-user support
- background jobs
- Google Trends
- Apify
- scraping non-official marketplaces in the core flow
- browser extension
- native iOS or Android app
- chat interface
- social features
- personalized wardrobe recommendations
- synthetic AI-generated listing photos
- marketplace messaging synchronization
- payment flows
- shipping workflows
- offer negotiation logic

## Stretch Goals Only If Core Flow Is Done
- inventory gallery page
- listing management dashboard
- Marketplace publish
- valuation confidence explanations
- history of valuation snapshots
- export package formats for more marketplaces
- platform status badges

---

## 6. User Experience Specification

## UX Principles
- mobile-first
- simple
- polished
- visual
- obvious
- fast-feeling
- minimal user effort
- no clutter

## Entry Experience
The homepage should immediately communicate:
- what AfterBuy is
- what the user can do
- the first action to take

The first action should support both:
- upload an item photo
- take a photo with the camera on supported mobile devices

## Processing Experience
The user should feel like the system is doing meaningful work.
There should be a clear progression:
- uploading image
- identifying item
- finding market comps
- estimating value
- generating listing

Avoid generic spinners only.
Use progress labels or staged loading indicators.

## Result Experience
The result page should be clearly segmented into:
1. uploaded item
2. extracted details
3. comparable listings
4. valuation summary
5. generated listing
6. review and edit section
7. publish/distribution actions
8. action buttons

## Design Goal
The product should feel like a modern consumer app, not a hacky admin dashboard.

---

## 7. Technical Architecture

## High-Level Architecture
The system consists of:
- a Next.js frontend
- a FastAPI backend
- Supabase for database and image storage
- OpenAI for vision extraction and listing generation
- SerpApi for comparable market item data

## Frontend Responsibilities
- render landing page
- handle image selection/upload
- show processing states
- display extracted item attributes
- display comparable listings
- display valuation
- display generated listing
- trigger optional publish action
- present results in a mobile-first way

## Backend Responsibilities
- receive uploaded image
- upload image to Supabase Storage
- store item row in database
- call OpenAI for extraction
- normalize extracted fields
- call the market data provider for comparables
- normalize comp records
- compute valuation range
- call OpenAI to generate listing copy
- persist valuation and listing records
- optionally publish to a supported marketplace

## Wear Assessment Layer
AfterBuy should include a visible wear assessment layer for wardrobe items.

This layer should:
- inspect wardrobe-relevant wear zones based on item type
- detect visible wear signals conservatively
- estimate wear severity and confidence
- produce a pricing adjustment factor
- improve listing realism and photo guidance

This is not a claim about true total condition.
It is an estimate of visible wear from the provided images only.

## Persistence Responsibilities
Supabase should store:
- item records
- image URLs
- extracted metadata
- comparable listings
- valuation results
- generated listing outputs
- optional publish statuses

## Environment Configuration
Runtime environment files are split by app:
- `frontend/.env.local` for public-safe frontend variables
- `backend/.env` for backend secrets
- root `.env.example` serves as the project template

---

## 8. Data Model

## items
Represents an owned item uploaded by the user.

Suggested fields:
- id
- created_at
- image_url
- source_type
- input_text
- brand
- category
- item_type
- title_guess
- color
- condition
- confidence_score
- extracted_metadata_json

### Wear Assessment Storage
Visible wear assessment should be stored inside `extracted_metadata_json` unless a separate field is clearly necessary.

Suggested nested structure:
- wear_level
- wear_confidence
- wear_summary
- pricing_adjustment_factor
- wear_signals

Each wear signal may include:
- zone
- signal
- severity
- confidence

## market_comps
Represents normalized comparable listings found on a marketplace.

Suggested fields:
- id
- item_id
- created_at
- source
- comp_title
- comp_price
- currency
- comp_url
- comp_condition
- comp_image_url
- similarity_score
- raw_json

## valuations
Represents the engine’s value estimate for an item.

Suggested fields:
- id
- item_id
- created_at
- estimated_low
- estimated_mid
- estimated_high
- suggested_listing_price
- confidence
- valuation_reason
- valuation_method
- comp_count

## generated_listings
Represents AI-generated listing content.

Suggested fields:
- id
- item_id
- created_at
- platform
- title
- description
- condition_note
- suggested_price
- attributes_json
- generation_reasoning

## listing_publications
Optional if marketplace publish is implemented.

Suggested fields:
- id
- item_id
- created_at
- platform
- publication_status
- external_listing_id
- external_listing_url
- raw_response_json

---

## 9. API Surface

## Required Backend Endpoints

### GET /
Purpose:
Health check for backend.

Response:
Simple JSON indicating backend is running.

### POST /extract-item
Purpose:
Accept image upload, store image, run OpenAI extraction, create item record.

Input:
multipart/form-data with image file

Output:
- item_id
- image_url
- extracted metadata

### POST /find-comps
Purpose:
Use extracted metadata to query a market data provider for comparable listings.

Input:
- item_id or extracted metadata payload

Output:
- normalized comparable listings
- comp count

### POST /valuate-item
Purpose:
Compute valuation from comps and item attributes.

Input:
- item_id or item metadata + comp payload

Output:
- low, mid, high range
- suggested listing price
- confidence
- valuation reason

### POST /generate-listing
Purpose:
Generate marketplace-ready title and description using OpenAI.

Input:
- item_id or item metadata + valuation

Output:
- title
- description
- condition note
- suggested price

### GET /item/{item_id}
Purpose:
Return a full assembled view model for the frontend.

Output:
- item
- comps
- valuation
- generated listing
- optional publication info

### Optional: POST /publish/marketplace
Purpose:
Create/publish a listing to a supported marketplace.

Input:
- item_id or generated listing payload

Output:
- publication status
- marketplace reference

---

## 10. Valuation Engine Specification

## Goal
The valuation engine must feel believable, stable, and explainable.
It does not need to be perfect or market-grade.

## Core Philosophy
Prefer simple, robust heuristics over fake sophistication.

## Inputs
- extracted item metadata
- comparable market listings
- condition estimate
- optional user-supplied purchase context

## Valuation Method
1. retrieve comparables
2. normalize and clean comp prices
3. score similarity
4. remove or downweight poor matches and outliers
5. compute a central estimate
6. widen into low and high bounds
7. produce confidence score
8. produce human-readable reason

## Similarity Dimensions
- title overlap
- brand match
- category match
- item type match
- color overlap if relevant
- overall metadata confidence

## Heuristic Approach
- exact or near-exact brand/title matches should weigh most
- broader category matches should weigh less
- outliers should not dominate pricing
- sparse or weak comps should lower confidence

## Required Outputs
- estimated_low
- estimated_mid
- estimated_high
- suggested_listing_price
- confidence
- valuation_reason

## Wear-Aware Adjustment
The valuation engine may apply a conservative visible-wear adjustment after comp-based estimation.

Suggested behavior:
- derive a wear adjustment factor from visible wear assessment
- apply that factor after comp weighting and condition heuristics
- reflect the adjustment honestly in the valuation reason

This adjustment should remain conservative and should never pretend to know hidden condition issues.

## Confidence Levels
- high: many strong matches
- medium: some decent but imperfect matches
- low: sparse data or mostly fallback logic

## Required Transparency
If the engine is uncertain, the UI and API must reflect that uncertainty honestly.

Do not present low-confidence outputs as precise facts.

---

## 11. AI Behavior Specification

## OpenAI Extraction Requirements
The extraction step must return structured JSON.
It must not return free-form prose.

Required fields:
- brand
- item_type
- category
- likely_product_name
- color
- visible_condition
- notable_details
- confidence

If uncertain:
- return null or low-confidence values rather than hallucinating

### Visible Wear Assessment Requirements
The extraction step should also return a structured visible wear assessment for wardrobe-relevant categories.

The wear assessment must:
- only describe wear that is visibly supported by the provided image(s)
- use lower confidence when the image quality is poor or important zones are not visible
- avoid guessing hidden condition issues
- avoid inferring age, wash history, odor, softness loss, or invisible defects

Required fields:
- wear_level
- wear_confidence
- wear_summary
- pricing_adjustment_factor
- wear_signals

If wear cannot be assessed confidently:
- return `unknown` or equivalent conservative output
- avoid strong pricing penalties

## OpenAI Listing Generation Requirements
The listing generator must produce:
- a concise marketplace-style title
- a factual description
- a condition note
- a suggested price reference if useful

The copy must:
- be clear
- be believable
- avoid hype
- avoid fake specifics
- avoid pretending to know hidden details not visible in the image

The copy must not:
- overclaim authenticity
- invent materials
- invent measurements unless explicitly known
- invent a SKU or season
- include spammy promotional language

---

## 12. Design System Expectations

## Frontend Stack
- Next.js
- Tailwind CSS
- shadcn/ui
- Recharts only if a chart adds real value

## Design Constraints
- no cluttered dashboards
- avoid overly dense tables
- use cards and clearly separated sections
- make primary action obvious
- typography should be clean and modern
- spacing should be generous on mobile
- loading states should look intentional

## Tone of UI
Simple, premium, consumer-facing.

---

## 13. Deployment and Demo Strategy

## Development
- frontend runs locally on port 3000
- backend runs locally on port 8000

## Deployment Priority
- deploy frontend on Vercel
- backend can remain local for demo if needed
- deploy backend only if time permits and it is stable

## Demo Priority
The demo must optimize for reliability over breadth.

Preferred demo should use:
- known good image
- known good comp retrieval case
- stable internet
- clean UI
- one polished flow

## Phone Demo Requirement
The frontend should be deployable to Vercel for phone testing and live demo sharing.

If backend deployment is not feasible in time, the team should still prioritize:
- frontend deployment
- mobile browser testing
- camera capture validation on phone

---

## 14. Implementation Phases

## Phase 0
Scaffold and repo hygiene

## Phase 1
Supabase setup and persistence foundation

## Phase 2
Upload and extraction flow

## Phase 3
Market comparable search

## Phase 4
Valuation engine

## Phase 5
Listing generation

## Phase 6
Result page assembly

## Phase 7
Review, edit, and mock marketplace publish

## Phase 8
Inventory, listing tracking, camera capture, and polish

## Phase 9
Wardrobe wear detection and wear-aware resale

---

## 15. Risks and Mitigation

## Risk: OpenAI extraction is messy
Mitigation:
Use structured outputs and conservative prompts.

## Risk: market comps are noisy
Mitigation:
Normalize and filter aggressively.
Use confidence scoring.

## Risk: UI becomes too dashboard-like
Mitigation:
Keep the UX upload-first and result-focused.

## Risk: publish flow consumes too much time
Mitigation:
Make publish optional and only after the core flow is complete.

## Risk: building too much
Mitigation:
Stay tightly aligned to the golden path.

---

## 16. Acceptance Criteria

The project is acceptable for demo if:
- homepage works
- image upload works
- extraction works
- comps are shown
- valuation is shown
- listing is generated
- UI looks polished on mobile
- data is persisted
- no critical crash occurs on the golden path

The project is excellent if:
- optional marketplace publish also works
- there is a simple inventory or listing status page
- the demo feels smooth and premium

---

## 17. Final Principle

The project should optimize for:
clarity + believability + end-to-end functionality

Not:
breadth + overengineering + too many integrations