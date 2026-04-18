# AfterBuy Tasks

## 1. Task Execution Rules

These rules are mandatory.

1. Work strictly in phase order.
2. Do not start a later phase until the current phase is verified.
3. Do not make speculative architecture changes unless required by the current phase.
4. Do not add features outside the scope defined in PLAN.md.
5. Every phase must conclude with:
   - code changes
   - manual verification instructions
   - any environment variable requirements
   - a short summary of what was implemented
6. If a task is blocked by an external dependency, implement the cleanest mockable boundary and stop.
7. If a task introduces a risky integration, isolate it behind a service layer.
8. No auth.
9. No Google Trends.
10. No Apify.
11. No additional marketplace posting beyond the stated scope unless explicitly approved.
12. No unnecessary package additions.

### Mandatory Approval Gate
At the end of each phase, stop implementation and wait for explicit user approval before starting the next phase.

For every phase completion message, include:
- phase name and number
- completed tasks
- files changed
- commands to run
- manual verification steps
- gate status: pass or fail
- any blockers, risks, or incomplete items

Do not start the next phase unless the user explicitly says to continue.

---

## 2. Development Standards

### Backend
- route handlers should remain thin
- service functions should contain core logic
- all external API access should go through service modules
- environment variables must be loaded via explicit config helpers
- JSON responses should be structured and predictable
- errors should be surfaced clearly

### Frontend
- mobile-first
- no clutter
- small, reusable components
- use semantic loading states
- no dead routes
- avoid unnecessary client-side state complexity

### Database
- define schema intentionally
- keep naming consistent
- do not add tables that are not needed for the MVP
- every persisted record should support the demo flow

---

## 3. Phase 0: Scaffolding and Repo Hygiene

### Objective
Establish a clean repo, frontend base, backend base, environment strategy, and ignore rules.

### Required Tasks

#### T0.1 Create root repo hygiene files
- create `.gitignore`
- ensure `.env.example` exists
- ensure secrets are not committed
- update root `README.md` with brief project identity

#### T0.2 Confirm frontend scaffold
- verify Next.js app runs
- confirm Tailwind is functioning
- verify package.json is sane
- keep frontend folder structure readable

#### T0.3 Install frontend UI dependencies
- install `lucide-react`
- install `recharts`
- initialize `shadcn/ui`
- add only needed shadcn components at this stage

#### T0.4 Create backend scaffold
- create Python virtual environment
- install FastAPI and core backend dependencies
- create `backend/app/main.py`
- create backend folders:
  - `app/routes`
  - `app/services`
  - `app/models`
  - `app/core`

#### T0.5 Backend health route
- add root health endpoint
- verify backend starts on port 8000

#### T0.6 Create root architecture docs if needed
- ensure PLAN, TASKS, TESTS, CLAUDE exist
- do not create extra docs unless useful

#### T0.7 Runtime environment files
- create `frontend/.env.local` for frontend-safe values
- create `backend/.env` for backend-only secrets
- keep root `.env.example` as the shared template only
- verify secret keys are never referenced from frontend code

### Deliverables
- working frontend scaffold
- working backend scaffold
- repo hygiene files in place

### Gate 0 Exit Criteria
- frontend runs successfully
- backend runs successfully
- `.gitignore` blocks env and build artifacts
- no secrets committed
- runtime env file structure is established:
  - `frontend/.env.local`
  - `backend/.env`
- root `.env.example` documents expected variables

---

## 4. Phase 1: Supabase Foundation

### Objective
Set up persistence and storage for uploaded items and generated outputs.

### Required Tasks

#### T1.1 Backend config module
- create a backend config helper
- load env vars safely
- validate required env vars on startup or first use

#### T1.2 Supabase service client
- implement a reusable Supabase client helper
- separate read and privileged operations if needed

#### T1.3 Storage setup logic
- support image upload to the configured bucket
- return stored image URL or retrievable URL

#### T1.4 Database schema design
Create SQL or migration definitions for:
- `items`
- `market_comps`
- `valuations`
- `generated_listings`
- optional `listing_publications`

#### T1.5 Persistence helpers
Implement service functions for:
- create item
- update extracted metadata
- insert comps
- insert valuation
- insert generated listing
- fetch assembled item by id

#### T1.6 Basic integration verification
- manually verify image upload path to Supabase
- manually verify DB inserts and reads

### Constraints
- do not implement auth tables
- do not create unnecessary relational complexity
- do not overbuild repository patterns

### Deliverables
- working Supabase connection
- image upload support
- persistent database tables
- basic CRUD helpers needed for later phases

### Gate 1 Exit Criteria
- an image can be uploaded to storage
- an item record can be created
- an item record can be read back
- schema supports all core later phases

---

## 5. Phase 2: Upload and OpenAI Extraction

### Objective
Create the first magical user interaction: upload an item image and receive structured extracted details.

### Required Tasks

#### T2.1 Frontend landing page
- create a clear homepage with product title and upload CTA
- mobile-first layout
- concise copy explaining value proposition

#### T2.2 Upload UI
- support image file selection
- validate file presence and basic type
- show upload progress or processing state

#### T2.3 Backend upload endpoint
- implement `POST /extract-item`
- accept multipart form image
- upload image to Supabase Storage
- create initial item row
- call extraction service

#### T2.4 OpenAI extraction service
- implement structured output extraction using OpenAI
- extract:
  - brand
  - item_type
  - category
  - likely_product_name
  - color
  - visible_condition
  - notable_details
  - confidence
- handle uncertainty conservatively
- avoid hallucinated specifics

#### T2.5 Metadata persistence
- store extraction results on item record
- preserve raw extracted JSON if useful

#### T2.6 Frontend extraction results display
- show uploaded image
- show extracted attributes in clean cards
- show confidence

#### T2.7 Loading and error states
- render distinct processing stages
- show clean user-facing errors

### Constraints
- extraction must return structured JSON
- do not embed comp lookup in this phase unless needed for a temporary stub
- do not build result page complexity yet beyond extraction outcome

### Deliverables
- end-to-end upload and extraction flow

### Gate 2 Exit Criteria
- user uploads image
- backend stores image
- backend extracts item metadata
- frontend displays believable result
- item data is persisted

---

## 6. Phase 3: Market Comparable Search

### Objective
Retrieve and normalize comparable marketplace listings for the extracted item.

### Required Tasks

#### T3.1 Market data provider client
- create dedicated market data service module
- implement provider authentication if required
- isolate provider-specific logic from route handlers

#### T3.2 Search strategy design
Implement ordered search behavior:
1. exact title guess + brand
2. broader title guess
3. brand + category + item type
4. category fallback

#### T3.3 Response normalization
Normalize each comp into a clean internal shape:
- title
- price
- currency
- URL
- image URL if present
- condition if present
- source

#### T3.4 Comp filtering
- remove clearly bad or empty entries
- ignore items with missing price
- drop obviously irrelevant categories where possible

#### T3.5 Persist comps
- store top comparable listings in DB
- keep raw JSON if useful for debugging

#### T3.6 Frontend comps section
- add a comparable listings card section
- display 3 to 6 strongest comps
- include title, image, price, and outbound link

### Constraints
- do not use scraping in this phase
- do not add Google Trends
- do not implement comp ranking with heavy ML
- keep normalization simple and strong

### Deliverables
- comparable listings retrieval from market data provider
- normalized comparable cards in UI

### Gate 3 Exit Criteria
- backend retrieves market comps for a known good item
- comps are normalized and stored
- frontend displays comps cleanly

---

## 7. Phase 4: Valuation Engine

### Objective
Produce a credible resale value estimate from the item and comparable listings.

### Required Tasks

#### T4.1 Similarity scoring utility
Create a simple scoring utility that considers:
- brand match
- category match
- item type match
- title overlap
- notable attribute overlap

#### T4.2 Outlier filtering utility
Implement a practical outlier filter:
- remove extreme high or low values
- ignore poor quality comps with low match score

#### T4.3 Core valuation calculation
Compute:
- estimated_low
- estimated_mid
- estimated_high
- suggested_listing_price

#### T4.4 Confidence logic
Set confidence to:
- high
- medium
- low

Confidence should be based on:
- number of comps
- comp quality
- exactness of metadata match
- use of fallback logic

#### T4.5 Reason generation
Create a short, deterministic explanation string such as:
- "Based on 5 strong comparable market listings"
- "Estimate is lower confidence due to sparse exact matches"

#### T4.6 Persistence
Store valuation record in DB.

#### T4.7 Frontend valuation card
Show:
- valuation range
- suggested listing price
- confidence badge
- short reason

### Constraints
- do not fake precise pricing certainty
- do not claim exact market truth
- do not add trend modeling yet
- keep math understandable and reviewable

### Deliverables
- working valuation engine
- valuation data stored and displayed

### Gate 4 Exit Criteria
- valuation is produced for known demo items
- confidence changes appropriately based on comp quality
- frontend displays valuation clearly

---

## 8. Phase 5: Listing Generation

### Objective
Generate marketplace-ready listing content using extracted metadata and valuation.

### Required Tasks

#### T5.1 Listing generation service
Create a dedicated OpenAI listing generation service.

#### T5.2 Prompt design
The prompt must use:
- extracted item metadata
- condition
- valuation range
- suggested listing price
- optionally comp summary context

The prompt must instruct the model to:
- stay factual
- avoid fake specifics
- avoid hype
- produce clean marketplace-style copy

#### T5.3 Required output fields
- title
- description
- condition note
- optional tags or attributes JSON

#### T5.4 Persistence
Store generated listing in DB.

#### T5.5 Frontend listing preview card
Display:
- listing title
- listing description
- condition note
- suggested price
- copy buttons

#### T5.6 Export action
Provide at least simple copy/export actions.

### Constraints
- do not generate fake authenticity claims
- do not fabricate measurements or material details
- do not use spammy or salesy tone
- output should feel suitable for real marketplace use

### Deliverables
- high-quality listing generation
- polished listing preview

### Gate 5 Exit Criteria
- generated listings read naturally
- generated listings are grounded in actual extracted data
- frontend listing card is polished and usable

---

## 9. Phase 6: End-to-End Result Page

### Objective
Assemble the complete user journey in one coherent experience.

### Required Tasks

#### T6.1 Assembled item endpoint
Implement `GET /item/{item_id}` returning:
- item
- comps
- valuation
- generated listing
- optional publication metadata

#### T6.2 Result page route
Create a result page that:
- loads the assembled item
- displays all sections in order
- handles refresh safely

#### T6.3 Processing orchestration
Decide frontend orchestration pattern:
- either call backend sequentially from frontend
- or create backend orchestration endpoint
Choose whichever is simpler and more reliable

#### T6.4 Loading UI
Show progress through:
- extracting item
- finding comps
- estimating value
- generating listing

#### T6.5 Error recovery UI
If comps fail:
- show extraction and a graceful fallback message

If valuation is low-confidence:
- show valuation honestly with low-confidence badge

If listing generation fails:
- preserve earlier successful outputs and show retry path

### Constraints
- do not collapse the UX into a confusing multi-step internal state machine
- keep the result page visually ordered and intuitive
- do not overcomplicate routing

### Deliverables
- complete end-to-end result page
- resilient UX for golden path and basic fallback cases

### Gate 6 Exit Criteria
- one complete path works from upload to result
- page refresh does not destroy the result
- result page is demo-ready on mobile

---

## 10. Phase 7: Optional Marketplace Publish Flow

### Objective
Allow AfterBuy to publish the generated listing to a supported marketplace if feasible.

### Required Tasks

#### T7.1 Research implementation boundary
- confirm credential needs
- confirm seller requirements
- define minimal publishable path

#### T7.2 Publication service
Create a marketplace publication service module isolated from other logic.

#### T7.3 Publish endpoint
Implement `POST /publish/marketplace`

#### T7.4 Publication state persistence
Store:
- publication_status
- external_listing_id
- external_listing_url if available
- raw response JSON for debugging

#### T7.5 Frontend publish action
Add a publish button to listing preview
Show:
- loading state
- success state
- failure state

### Constraints
- if real publishing is too complex, stop and do not derail the MVP
- if mocking is necessary, it must be clearly labeled
- do not implement this before core flow is stable

### Deliverables
- real or clearly labeled mock publish flow

### Gate 7 Exit Criteria
- publish flow works or is intentionally deferred without harming MVP

---

## 11. Phase 8: Stretch Inventory / Listing Dashboard

### Objective
Show that AfterBuy can serve as a simple ownership and resale management layer.

### Required Tasks

#### T8.1 Inventory page
Display:
- item image
- title guess
- category
- valuation mid
- status badge

#### T8.2 Listing status page
Display:
- platform
- generated or published status
- suggested price
- quick actions

#### T8.3 Visual polish
- improve spacing
- improve mobile layout
- reduce UI rough edges

### Constraints
- dashboard must not become cluttered
- do not build this before the core demo is stable

### Deliverables
- optional inventory/listing pages

### Gate 8 Exit Criteria
- pages support the product story without distracting from core demo

---

## 12. Final Demo Preparation Tasks

### T9.1 Seed demo data
Prepare a few known-good item images.

### T9.2 Validate golden path
Run one full demo path multiple times.

### T9.3 Polish visible text
Refine labels, headings, button copy, and empty states.

### T9.4 Remove dead code
Delete abandoned experiments, unused routes, and unused components.

### T9.5 Final README update
Document:
- what AfterBuy does
- tech stack
- how to run locally
- environment variables
- any limitations

---

## 13. Stop Conditions

Claude must stop and ask for direction if:
- an external API is blocked
- publish flow requires substantial auth complexity
- a design choice would significantly expand scope
- proposed implementation conflicts with PLAN.md
- more than one implementation path is plausible and the choice materially affects architecture