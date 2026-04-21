# AfterBuy

AfterBuy is a mobile-first AI wardrobe resale agent for post-purchase commerce.

Upload or photograph something you own. AfterBuy identifies the item, estimates visible wear from the provided images, finds comparable market listings, adjusts resale value accordingly, generates a marketplace-ready listing, and lets you distribute it across selected channels — all in one flow.

## Demo Video
[![Watch the demo](https://img.youtube.com/vi/dyWOPRP8p90/hqdefault.jpg)](https://youtu.be/dyWOPRP8p90?si=LzaobKKVpE3TPyZa)

**Core flow:**
photo upload or camera capture → item extraction + visible wear assessment → market comparables → wear-aware resale valuation → generated listing → review/edit → channel distribution → inventory tracking

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js 15, TypeScript, Tailwind CSS, shadcn/ui |
| Fonts | Geist Sans (UI), DM Serif Display (display headings) |
| Backend | FastAPI (Python 3.11+) |
| Storage & DB | Supabase (Storage + Postgres) |
| AI — extraction | OpenAI GPT-4o vision (structured output) |
| AI — listing | OpenAI GPT-4o (structured output) |
| Market data | SerpApi (Google Shopping) |

---

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+
- Supabase project (free tier is fine)
- OpenAI API key
- SerpApi API key

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs on http://localhost:3000

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Runs on http://localhost:8000

---

## Environment Variables

### `backend/.env`

```env
OPENAI_API_KEY=your_openai_api_key_here

SUPABASE_URL=your_supabase_project_url_here
SUPABASE_SERVICE_KEY=your_supabase_service_role_key_here
SUPABASE_STORAGE_BUCKET=item-images

SERPAPI_API_KEY=your_serpapi_api_key_here
```

### `frontend/.env.local`

```env
NEXT_PUBLIC_BACKEND_URL=http://localhost:8000

NEXT_PUBLIC_SUPABASE_URL=your_supabase_project_url_here
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=your_supabase_anon_key_here
```

See `.env.example` in the repo root for the full template.

---

## Supabase Setup

Create the following tables in your Supabase project (SQL Editor):

```sql
create table items (
  id uuid primary key default gen_random_uuid(),
  created_at timestamptz default now(),
  image_url text,
  source_type text default 'photo',
  input_text text,
  brand text,
  category text,
  item_type text,
  title_guess text,
  color text,
  condition text,
  confidence_score float,
  extracted_metadata_json jsonb
);

create table market_comps (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id),
  created_at timestamptz default now(),
  source text,
  comp_title text,
  comp_price float,
  currency text default 'USD',
  comp_url text,
  comp_condition text,
  comp_image_url text,
  similarity_score float,
  raw_json jsonb
);

create table valuations (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id),
  created_at timestamptz default now(),
  estimated_low float,
  estimated_mid float,
  estimated_high float,
  suggested_listing_price float,
  confidence text,
  valuation_reason text,
  valuation_method text,
  comp_count integer
);

create table generated_listings (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id),
  created_at timestamptz default now(),
  platform text default 'generic',
  title text,
  description text,
  condition_note text,
  suggested_price float,
  attributes_json jsonb,
  generation_reasoning text,
  item_specifics_json jsonb,
  photo_checklist_json jsonb
);

create table listing_publications (
  id uuid primary key default gen_random_uuid(),
  item_id uuid references items(id),
  created_at timestamptz default now(),
  platform text,
  publication_status text,
  external_listing_id text,
  external_listing_url text,
  raw_response_json jsonb
);
```

Create a public storage bucket named `item-images` in Supabase Storage.

---

## Mobile Testing

For testing on a phone, deploy the frontend to Vercel (or use a tunneling tool like [ngrok](https://ngrok.com)) and point `NEXT_PUBLIC_BACKEND_URL` at your backend. Camera capture (`Take photo`) works natively on iOS Safari and Android Chrome.

---

## Demo Guide

### Recommended demo items

These item types consistently produce strong extraction, real comps, and believable valuations:

| Item | Why it works |
|---|---|
| **Branded fleece or jacket** (North Face, Patagonia, Arc'teryx) | Clear brand + type, active Poshmark/eBay market |
| **Sneakers** (Nike Air Max, Jordan 1, Adidas Samba) | Strong brand recognition, high-volume resale |
| **Water bottle** (Hydro Flask, Stanley, YETI) | Distinctive shape + branding, good comps |
| **Tote or backpack** (Herschel, Fjällräven, Coach) | Clear visual brand, good comparable data |

Avoid: generic unbranded items, low-resolution images, images without a clear subject.

### Golden path demo script

1. Open the app on the homepage
2. Tap **Take photo** (on phone) or **Upload photo** (on desktop)
3. Select or photograph a branded wardrobe item such as a jacket, sneaker, bag, or hoodie
4. Watch staged processing: Uploading → Identifying → Finding comps → Estimating value → Generating listing
5. On the result page:
   - Review extracted attributes, visible wear assessment, and confidence badges
   - Browse comparable market listings with prices and outbound links
   - See the valuation range and suggested listing price
   - Read the generated marketplace-ready listing
6. In the Review & Distribute panel:
   - Optionally tap **Edit** to revise the title, description, condition, or price
   - Select one or more channels (eBay, Poshmark, Depop, Facebook)
   - Tap **Distribute to N channels**
7. Navigate to **My items** to see the inventory view with status badges

### Demo narration anchor

> "Most commerce products stop at checkout. AfterBuy is the missing layer — after you buy something, after you own it, when you decide you're done with it. You take a photo. AfterBuy identifies it, prices it against real market data, and produces a listing you can actually post. In one flow."

---

## What is real vs simulated

| Feature | Status |
|---|---|
| Image upload and storage | Real — Supabase Storage |
| Item extraction (brand, type, color, condition) | Real — OpenAI GPT-4o vision |
| Market comparable listings | Real — SerpApi Google Shopping |
| Valuation engine | Real computation — weighted comp heuristic with IQR outlier removal |
| Listing generation | Real — OpenAI GPT-4o |
| Listing edit and persistence | Real — saved to Supabase |
| Channel distribution | Simulated — mock publication record per platform; no real marketplace API calls |
| Inventory tracking | Real — reads from persisted item and publication records |
| Visible wear assessment | Real — OpenAI GPT-4o vision; structured per-zone signals with severity + confidence scores; pricing adjustment applied conservatively in backend |

The distribution flow is intentionally simulated. Real marketplace publishing (eBay, Poshmark, etc.) requires seller account OAuth — out of scope for this MVP. The in-app copy reflects this honestly: "Listing routing is simulated for selected channels."

---

## API Overview

| Endpoint | Purpose |
|---|---|
| `GET /` | Health check |
| `GET /health` | Service configuration status |
| `POST /extract-item` | Upload image, run extraction, create item record |
| `POST /find-comps` | Fetch and persist comparable market listings |
| `POST /valuate-item` | Compute wear-aware valuation from comps |
| `POST /generate-listing` | Generate listing copy with OpenAI |
| `PATCH /listing/{id}` | Update listing after user edit |
| `GET /item/{item_id}` | Return assembled item state for result page |
| `POST /publish/marketplace` | Simulate channel distribution |
| `GET /items` | Return inventory list |

---

## Known Limitations

- **No authentication** — all items are shared in the same database. Fine for a single-user demo.
- **SerpApi dependency** — if quota is exhausted or the key is invalid, comps return empty and valuation/listing will not run.
- **Camera capture** requires HTTPS or localhost. Use a deployed URL or tunnel for reliable phone camera access.
- **Low-confidence items** — blurry, generic, or unbranded images may return low-confidence extraction and skip comps and valuation. This is intentional graceful degradation.
- **Channel distribution is simulated** — no real listings are created on any marketplace.
- **Visible wear is image-based only** — AfterBuy estimates visible wear from the provided photos. It does not know hidden defects, odor, wash history, elasticity loss, or internal condition.

---

## Project Docs

- [PLAN.md](PLAN.md) — product scope and architecture
- [TASKS.md](TASKS.md) — implementation phases and task list
- [TESTS.md](TESTS.md) — test and verification strategy
- [API_SPEC.md](API_SPEC.md) — backend API contract
- [CLAUDE.md](CLAUDE.md) — implementation rules
