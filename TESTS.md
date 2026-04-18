# AfterBuy Tests

## 1. Testing Philosophy

This is a hackathon MVP.
The testing goal is not maximum coverage.
The testing goal is confidence in the golden path.

Priority order:
1. end-to-end flow works
2. critical integrations work
3. UI does not break on mobile
4. failures are understandable
5. valuation and listing outputs are believable

Tests should be:
- lightweight
- practical
- phase-aligned
- focused on demo reliability

Every phase must include:
- manual verification
- at least lightweight programmatic validation where appropriate

---

## 2. Global Quality Standards

The project fails QA if any of the following are true on the main path:
- upload crashes
- extracted metadata is empty for a good image
- comps do not render for a good item
- valuation is missing or nonsensical
- listing generation returns unusable copy
- UI is broken on a phone-sized viewport
- critical secrets are committed to Git
- route errors are swallowed silently

The project is considered demo-ready if:
- one full flow works smoothly from upload to listing preview
- the UI is clean and understandable
- low-confidence outcomes are handled honestly

---

## 3. Phase 0 Tests: Scaffolding

### P0-T1 Repo Hygiene Test
Verify:
- `.env` is ignored
- `.env.*` is ignored except `.env.example`
- `node_modules`, `.next`, `venv`, and Python cache directories are ignored
- no secrets appear in Git status

### P0-T2 Frontend Boot Test
Command:
- run frontend dev server

Expected:
- frontend starts successfully
- local URL loads
- no fatal compile errors

### P0-T3 Backend Boot Test
Command:
- run FastAPI app with Uvicorn

Expected:
- backend starts successfully
- health endpoint returns success JSON

### P0-T4 Dependency Sanity Test
Verify:
- package install succeeded
- Python dependencies install without import errors
- no obvious package version conflicts

### Phase 0 Exit Test
Both frontend and backend must run simultaneously without errors.

---

## 4. Phase 1 Tests: Supabase Foundation

### P1-T1 Database Connectivity Test
Use a minimal backend route or script to verify:
- backend can connect to Supabase
- a test read or insert succeeds

### P1-T2 Storage Upload Test
Upload a sample image to Supabase Storage.

Expected:
- upload succeeds
- retrievable URL or accessible storage path is returned

### P1-T3 Table Insert Test
Insert:
- one item
- one valuation
- one generated listing
using stubbed or test data

Expected:
- records appear in the database
- foreign key relationships or references are valid

### P1-T4 Fetch-Assembled Data Test
Fetch item and related records.

Expected:
- assembled structure contains all expected sections
- missing relations do not crash the response

### Phase 1 Exit Test
The backend must be able to:
- upload image
- create item
- store related outputs
- read assembled item data back

---

## 5. Phase 2 Tests: Upload and Extraction

### P2-T1 Upload Endpoint Test
Send a real image to `POST /extract-item`.

Expected:
- status 200
- item_id returned
- image_url returned
- extracted metadata returned

### P2-T2 Structured Extraction Test
Verify extracted payload contains:
- brand or null
- category or null
- item_type or null
- title_guess or likely_product_name
- visible_condition
- confidence

Expected:
- payload is valid structured JSON
- no free-form rambling text

### P2-T3 Reasonable Extraction Test
Use a visually clear demo item.

Expected:
- category is believable
- title guess is plausible
- condition is plausible
- confidence is not absurdly high if item is ambiguous

### P2-T4 Corrupt File Test
Upload invalid or non-image file.

Expected:
- request fails gracefully
- user sees clear error
- backend does not crash

### P2-T5 Frontend Upload UX Test
Perform upload from browser.

Expected:
- loading state appears
- progress label appears
- successful extraction view renders cleanly

### Phase 2 Exit Test
One real image upload must work end-to-end through extraction and frontend display.

---

## 6. Phase 3 Tests: eBay Comparable Search

### P3-T1 eBay Service Smoke Test
Call eBay search service with a known query.

Expected:
- receives response
- no auth or parsing failure

### P3-T2 Normalization Test
Verify each comp includes:
- title
- price
- URL
- source
- optional image URL
- optional condition

Expected:
- normalized structure is consistent
- malformed entries are discarded

### P3-T3 Relevant Comp Test
Use a known item with reasonable resale presence.

Expected:
- at least a few comparable listings are returned
- obvious junk matches are limited

### P3-T4 Empty Result Test
Use a rare or ambiguous item.

Expected:
- no crash
- graceful fallback response
- later phases can still proceed in low-confidence mode if designed to

### P3-T5 Frontend Rendering Test
Verify comps section shows:
- image or placeholder
- title
- price
- source
- clickable outbound link if allowed

### Phase 3 Exit Test
Known good demo items must retrieve believable comps and show them in the UI.

---

## 7. Phase 4 Tests: Valuation Engine

### P4-T1 Deterministic Utility Test
Given a fixed comp set, valuation output should be stable.

Expected:
- same inputs produce same outputs

### P4-T2 Outlier Handling Test
Use comp data with one extreme outlier.

Expected:
- estimate is not dominated by that outlier

### P4-T3 Sparse Comp Test
Use only 1 to 2 weak comps.

Expected:
- valuation still returns
- confidence is low
- reason acknowledges low certainty

### P4-T4 Strong Comp Test
Use many strong comps.

Expected:
- confidence is higher
- reason reflects stronger evidence

### P4-T5 UI Valuation Test
Verify valuation card shows:
- low
- mid
- high
- suggested listing price
- confidence badge
- brief reason

### P4-T6 Sanity Range Test
Ensure:
- low <= mid <= high
- suggested listing price is not nonsensical
- negative or zero values are handled safely

### Phase 4 Exit Test
The valuation engine must return believable outputs for at least two demo items.

---

## 8. Phase 5 Tests: Listing Generation

### P5-T1 Listing Structure Test
Verify generated listing includes:
- title
- description
- condition note

### P5-T2 Grounding Test
Review generated listing.

Expected:
- no invented measurements
- no invented materials unless supported
- no invented authenticity claims
- no spammy wording

### P5-T3 Readability Test
Expected:
- title is concise
- description is organized
- tone is suitable for resale listing

### P5-T4 Price Consistency Test
Expected:
- suggested price aligns with valuation output
- listing does not contradict valuation

### P5-T5 Copy Button Test
Verify title and description copy actions work in UI.

### P5-T6 Persistence Test
Generated listing record must persist and be retrievable.

### Phase 5 Exit Test
The generated listing must feel like something a user could plausibly post.

---

## 9. Phase 6 Tests: Full End-to-End Flow

### P6-T1 Golden Path Test
Run the complete flow:
1. upload image
2. extract metadata
3. fetch comps
4. compute valuation
5. generate listing
6. render result page

Expected:
- no fatal errors
- data displayed in correct order
- result looks polished

### P6-T2 Refresh Persistence Test
Reload result page after completion.

Expected:
- page reconstructs from stored data
- no dependency on transient in-memory state

### P6-T3 Mobile Layout Test
Check on narrow viewport.

Expected:
- no broken layout
- no text overflow
- primary actions remain visible

### P6-T4 Partial Failure Test
Force or simulate one later-step failure.

Examples:
- comp fetch fails
- listing generation fails

Expected:
- earlier successful steps remain visible
- user sees a clean error and does not lose all progress

### P6-T5 Performance Perception Test
Expected:
- user always sees progress
- no unexplained waiting state longer than a few seconds without messaging

### Phase 6 Exit Test
The app must be demoable end-to-end on the golden path with confidence.

---

## 10. Phase 7 Tests: Optional eBay Publish

### P7-T1 Publish Service Smoke Test
Verify publish route can be invoked without server crash.

### P7-T2 Publish Result Test
If real publishing is implemented:
- verify response contains marketplace reference or success state

If mock publishing is used:
- verify UI and API clearly label it as mock

### P7-T3 UI Publish Test
Expected:
- publish button works
- loading state visible
- success/failure state shown clearly

### P7-T4 Persistence Test
Publication result should be stored in listing_publications if implemented.

### Phase 7 Exit Test
Real publish works or the feature is intentionally deferred without harming the MVP.

---

## 11. Stretch Tests: Inventory / Listing Dashboard

### P8-T1 Inventory Page Test
Expected:
- previously uploaded items render as cards
- titles, thumbnails, and valuation snippets appear correctly

### P8-T2 Listing Status Test
Expected:
- generated and published statuses show correctly
- layout remains uncluttered

### P8-T3 Navigation Test
Expected:
- moving between landing, result, and inventory pages is stable

---

## 12. Demo Readiness Checklist

The project is demo-ready only if all are true:

- homepage looks clean
- upload flow works
- known good image extracts correctly
- comps appear for known demo item
- valuation is believable
- generated listing is polished
- mobile viewport looks good
- no obvious console errors on golden path
- no secrets are exposed in frontend bundle
- at least one fallback case behaves gracefully

---

## 13. Required Manual Test Data

Prepare and keep ready:
- 2 to 3 good fashion item images
- 1 ambiguous image for fallback testing
- 1 invalid file to verify upload error handling

Preferred good items:
- jacket
- sneaker
- bag

Avoid obscure items for the main demo.

---

## 14. Non-Negotiable Verification Before Final Demo

Before showing anyone:
1. run frontend
2. run backend
3. run one full upload flow
4. reload result page
5. test on phone-sized viewport
6. verify no secrets are in repo status
7. verify the app text and labels are polished