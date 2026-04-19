# AfterBuy

AfterBuy is a mobile-first AI ownership agent for post-purchase commerce.

Upload or photograph something you own. AfterBuy identifies it, finds comparable market listings, estimates its resale value, generates a marketplace-ready listing, lets you review/edit it, and can mock-publish it across marketplaces while tracking status in one place.

## What it does

**photo upload or camera capture → item extraction → market comparables → resale valuation → generated listing → review/edit → mock marketplace publish → optional tracking dashboard**

## Tech Stack

- **Frontend:** Next.js, TypeScript, Tailwind CSS, shadcn/ui
- **Backend:** FastAPI (Python)
- **Storage & DB:** Supabase
- **AI:** OpenAI (vision extraction + listing generation)
- **Market data:** SerpApi (with mock fallback support if needed)

## Local Development

### Prerequisites

- Node.js 18+
- Python 3.11+

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

## Local Phone Testing (Same Wi-Fi)

To test on your phone over Wi-Fi before deployment:

### 1. Find your laptop's local IP

```bash
ipconfig getifaddr en0   # macOS Wi-Fi
# Example output: 192.168.1.42
```

### 2. Update `frontend/.env.local`

Replace `localhost` with your laptop IP:

```
NEXT_PUBLIC_BACKEND_URL=http://192.168.1.42:8000
```

### 3. Update `backend/.env`

Add a `CORS_ORIGINS` line that includes the LAN frontend origin:

```
CORS_ORIGINS=http://localhost:3000,http://192.168.1.42:3000
```

### 4. Run backend bound to all interfaces

```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Run frontend

```bash
cd frontend
npm run dev
# Next.js already binds to 0.0.0.0 by default
```

### 6. Open on your phone

Navigate to:
```
http://192.168.1.42:3000
```

Both devices must be on the same Wi-Fi network. Replace `192.168.1.42` with your actual laptop IP.

### Caveats

- Camera capture (`Take photo`) triggers the native camera on iOS Safari and Android Chrome. Upload from library also works on both.
- To revert to desktop-only, remove the `CORS_ORIGINS` line from `backend/.env` and restore `NEXT_PUBLIC_BACKEND_URL=http://localhost:8000` in `frontend/.env.local`.

---

## Environment Variables

Use `frontend/.env.local` for frontend-safe variables and `backend/.env` for backend secrets.

Use `.env.example` in the repo root as the shared template.

## Project Docs

- [PLAN.md](PLAN.md) — product scope and architecture
- [TASKS.md](TASKS.md) — implementation phases and task list
- [TESTS.md](TESTS.md) — test and verification strategy
- [API_SPEC.md](API_SPEC.md) — backend API contract
- [CLAUDE.md](CLAUDE.md) — implementation rules for Claude Code
