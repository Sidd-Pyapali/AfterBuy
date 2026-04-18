# Claude Code Instructions for AfterBuy

## 1. Mission

You are helping build AfterBuy, a hackathon MVP for the Autonomous Agents track.

AfterBuy is a mobile-first AI ownership agent that:
- accepts a photo of an owned item
- identifies the item using OpenAI
- fetches comparable market listings from a market data provider
- estimates resale value
- generates a marketplace-ready listing
- optionally publishes to a supported marketplace

Your job is to implement this product in tightly scoped phases without going outside the defined product and engineering boundaries.

---

## 2. Highest-Level Product Rules

These are absolute rules.

1. The product is not a marketplace.
2. The product is not a full resale SaaS.
3. The product is not a chatbot.
4. The product is not a closet social app.
5. The product is not a flipping or arbitrage tool.
6. The product is an AI ownership agent focused on post-purchase resale preparation.

If implementation choices start drifting toward unrelated product shapes, stop and realign to this.

---

## 3. Core User Story

The main user story is:

A user has an item they already own.
They upload a photo.
AfterBuy identifies the item, estimates its resale value using market comps, and generates a listing they can use to sell it.

Everything should optimize for this one story first.

---

## 4. Hard Scope Constraints

You must not add the following unless explicitly instructed:
- authentication
- Google Trends integration
- Apify integration
- multi-marketplace live publishing beyond approved scope
- browser extension support
- native mobile app
- social features
- real-time notifications system
- inbox syncing with marketplaces
- background jobs
- queue systems
- recommendation engine
- wardrobe planner
- synthetic AI image generation for listings
- advanced ML training pipelines
- vector database unless explicitly needed
- excessive package additions
- speculative abstractions

Do not “future-proof” the app by building large systems that are not necessary for the MVP.

---

## 5. Implementation Philosophy

### Primary Goal
Ship a polished, believable, end-to-end demo.

### Secondary Goal
Keep architecture clean enough that the app does not collapse under small changes.

### Never Optimize For
- overengineering
- premature abstraction
- too many integrations
- unnecessary elegance
- hidden complexity

### Preferred Pattern
Simple explicit code that is easy to debug.

---

## 6. Repo Structure Rules

The repo is a monorepo with:
- `frontend/` for Next.js
- `backend/` for FastAPI
- docs in root markdown files

Respect this structure.

Do not create a sprawling nested architecture.
Do not create many internal packages.
Do not restructure without strong reason.

---

## 7. Frontend Rules

### Stack
Use:
- Next.js
- TypeScript
- Tailwind CSS
- shadcn/ui
- Recharts only if justified
- lucide-react for icons if needed

### Design Rules
- mobile-first
- premium consumer feel
- clear upload-first interaction
- no dense enterprise dashboards
- use cards and well-spaced sections
- typography should be clean and restrained
- no unnecessary complexity in animations

### UX Rules
The user should always understand:
- what the app is doing
- what step they are on
- what result was produced
- what action they can take next

### Component Rules
- keep components focused and readable
- avoid giant page files if they become unwieldy
- do not create dozens of tiny abstraction-only components
- use client components only when needed

### State Rules
- keep state simple
- do not introduce complex state libraries unless absolutely necessary
- local state and fetch-based flows are preferred

---

## 8. Backend Rules

### Stack
Use:
- FastAPI
- Python
- service modules for integrations
- route modules for endpoint definitions

### Route Design Rules
- routes should be thin
- services should hold external API logic and business logic
- return clean JSON
- errors should be explicit

### Error Handling Rules
- never swallow errors silently
- return useful but concise error messages
- preserve debuggability in logs
- keep user-facing errors readable

### Config Rules
- all secrets must come from env vars
- env vars should be loaded in a dedicated config helper
- do not hardcode secrets or URLs

### Environment File Rules

Use these runtime environment files:

- `frontend/.env.local` for frontend-safe public variables only
- `backend/.env` for backend-only secrets

Use the root `.env.example` only as a template and documentation artifact.

Never put backend secrets in frontend environment files.
Never expose:
- `OPENAI_API_KEY`
- Supabase secret/service role key
- marketplace or scraping provider secret keys

Frontend may only use public-safe variables such as:
- `NEXT_PUBLIC_BACKEND_URL`
- `NEXT_PUBLIC_SUPABASE_URL`
- `NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`

---

## 9. AI Integration Rules

### OpenAI Usage
OpenAI is the provider for:
- image extraction
- listing generation

### Extraction Rules
Extraction must:
- produce structured JSON
- be conservative under uncertainty
- avoid hallucinating unsupported specifics

Expected extraction fields:
- brand
- item_type
- category
- likely_product_name
- color
- visible_condition
- notable_details
- confidence

If the model is uncertain, lower confidence or use null-like values rather than inventing facts.

### Listing Generation Rules
Listing generation must:
- be factual
- be concise
- be suitable for resale marketplaces
- avoid fake specifics
- avoid marketing fluff
- avoid unverifiable claims

Never:
- invent measurements
- invent exact materials unless strongly supported
- invent authenticity guarantees
- invent SKU or collection details
- use spammy text like “must see” or “rare find” unless explicitly justified

---

## 10. Marketplace Integration Rules

### Market Data Provider
Use a market data provider such as SerpApi for comparable market listings.

Use the provider for:
- comparable market listings
- normalized product and pricing data
- fallback-ready integration behind a service boundary

### Marketplace Publishing
Do not implement full cross-posting now.
You may create export-ready structures for other marketplaces only if time permits and if clearly non-core.

### Publishing Rule
Do not allow the optional marketplace publish flow to derail the MVP.
If it becomes too complex, isolate it and leave it as an optional stretch or clearly labeled mock flow.

---

## 11. Database and Persistence Rules

Use Supabase for:
- item records
- image storage
- comps
- valuations
- generated listings
- optional publication records

Rules:
- persist core outputs
- do not rely only on transient frontend memory
- keep schema simple and purposeful
- do not create unused tables

---

## 12. Valuation Engine Rules

The valuation engine must be:
- simple
- explainable
- confidence-aware
- comp-based

Do:
- normalize comparable listings
- score similarity with practical heuristics
- filter outliers
- produce low, mid, high
- provide confidence and reason

Do not:
- overclaim precision
- use fake trend science
- make unsupported algorithmic claims
- build complex predictive models in this MVP

If confidence is low, say so clearly.

---

## 13. Required Development Workflow

You must work in phases.

### Phase Order
1. scaffold and hygiene
2. Supabase foundation
3. upload and extraction
4. market comparables
5. valuation engine
6. listing generation
7. result page assembly
8. optional marketplace publish
9. optional dashboard polish

Do not skip ahead.

Before moving to a new phase, confirm:
- what was implemented
- what files changed
- how to run it
- how to verify it manually

---

## 14. What You Must Report After Each Phase

After each completed phase, provide:
1. summary of what was built
2. files added/changed
3. any required env vars
4. how to run the feature
5. manual test steps
6. known limitations

Do not just dump code with no explanation.

---

## 15. When To Stop And Ask

You must stop and ask for direction if:
- an integration requires a major scope expansion
- a change would significantly alter architecture
- the publish flow demands large unplanned auth work
- there are multiple plausible implementation paths with meaningful tradeoffs
- a required env var or external setup is missing
- a dependency failure blocks reliable implementation

Do not guess blindly on major architecture or product decisions.

---

## 16. Coding Style Rules

### General
- keep code readable
- prefer explicit over clever
- avoid over-abstraction
- avoid dead code
- add comments only where useful
- use clear function and variable names

### Backend
- separate services by responsibility
- prefer pure utility functions where possible
- keep request parsing and business logic separate

### Frontend
- keep pages readable
- extract sections into components when useful
- do not create unnecessary design system complexity

---

## 17. UI Content Rules

The product copy should reinforce:
- ownership
- value recovery
- resale simplicity
- post-purchase intelligence

Avoid wording that implies:
- speculative investing
- fashion flipping
- social commerce
- hype-driven resale culture

Good phrasing:
- estimate value
- ready to resell
- marketplace-ready listing
- understand what your item is worth
- turn ownership into action

Bad phrasing:
- flip for profit
- arbitrage
- hunt hype drops
- maximize speculative gains

---

## 18. Demo-First Rules

Always optimize implementation toward the final demo.

That means:
- prioritize one strong upload-to-listing flow
- choose reliability over feature breadth
- make the UI easy to narrate
- ensure the output looks polished
- avoid building hidden complexity that is not visible to judges

The judges will care more about:
- technical credibility
- clarity
- novelty
- polished execution

Than about:
- number of integrations
- complexity for its own sake

---

## 19. File and Folder Expectations

Expected important files include:
- frontend app pages/components
- backend main app
- backend services for:
  - OpenAI extraction
  - OpenAI listing generation
  - Market comparable retrieval
  - valuation
  - Supabase persistence

Keep service boundaries clear.

Do not merge all logic into one giant file.

---

## 20. Non-Negotiable Safety and Quality Rules

- never commit secrets
- never expose server-side secrets to frontend
- never fabricate user data
- never fabricate marketplace IDs
- never fake a real publish if it is mock
- never present low-confidence valuations as precise facts

Honesty and clarity matter.

---

## 21. Mandatory Check-In and Approval Gate

After each phase, you must stop and wait for explicit user approval before moving to the next phase.

You must not begin a new phase automatically.

At the end of every phase, provide a structured check-in with:
1. summary of what was built
2. files added or modified
3. any required environment variables
4. exact commands to run locally
5. manual verification steps
6. whether the phase exit criteria in TASKS.md are fully satisfied
7. any known limitations or blockers

If any task in the current phase is incomplete, say so explicitly and do not claim the phase is done.

If the current phase passes, ask for approval to proceed.

Never continue from Phase N to Phase N+1 without explicit user confirmation.

---

## 22. Final Principle

If there is ever a conflict between:
- building more features
and
- preserving a clean, believable, demoable golden path

Choose the clean, believable, demoable golden path.