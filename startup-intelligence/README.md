# Startup Intelligence — Multi-Agent AI Due Diligence Advisor

## What changed in this pass

### Fixed
- **`requirements.txt` was empty.** Filled it in with the packages the code actually imports (`fastapi`, `uvicorn`, `pydantic`, `python-dotenv`, `google-genai`, `tavily-python`).
- **No CORS.** A browser-based frontend running on a different origin (a local file, a dev server, or a hosted page) was blocked from calling the API. Added `CORSMiddleware`.
- **`/startup` could crash the request with a raw 500 and no message.** Wrapped the orchestrator call in a `try/except` that returns a readable error instead.
- Removed a stray duplicate `backend/competitor.py` left outside `app/agents/` (the real one already lives in `app/agents/competitor.py`) and the committed `.venv/` and `__pycache__` folders.

I checked `app/tools/llm.py`'s use of `client.interactions.create(...)` / `interaction.output_text` — this looked at first like a mistaken call, but it matches Google's newer **Interactions API** for Gemini, so I left it as is.

### Added
- **`app/db.py` — SQLite persistence.** Every `/startup` run is now saved (id, timestamp, input, full analysis). New endpoints:
  - `GET /startups` — list saved reports
  - `GET /startups/{id}` — fetch one full report
  - `DELETE /startups/{id}` — remove one
  This is a genuine, working piece of the "Database" item from the roadmap — but it's **SQLite, not PostgreSQL**. It's a zero-setup stand-in so the app is actually usable today; every query goes through `db.py`'s functions, so swapping in real PostgreSQL later means replacing that one file, not touching the rest of the app.
- **A frontend dashboard** (published separately — see the link above the file list) that calls this API: a form to submit a startup idea, an animated "agents working" pipeline view while the analysis runs, a tabbed report (one tab per agent plus a Final Report tab), and a history sidebar backed by the new `/startups` endpoints.
- `.env.example` and `.gitignore` (the real `.env` should never be committed).

### Verified, not just written
I actually ran the backend in a sandbox (with the Gemini/Tavily calls stubbed out, since I can't reach those hosts from here) and confirmed: server boots, `/startup` runs the full 10-agent pipeline end-to-end, the SQLite table is created and a report is saved and re-fetchable, and the CORS preflight returns the right header. That gave me real confidence the fixes work, not just that they look right.

## What is still genuinely not done

Being direct about this, per the project's own rule of not exaggerating status: the items below are **planned, not implemented**. I did not attempt them in this pass — each is a substantial piece of work on its own (new infra, credentials, or a build pipeline I can't fully test from here), so shipping a half-working version silently would be worse than being clear about the gap:

| Area | Status |
|---|---|
| PostgreSQL (cloud) | Not done — SQLite added instead, see above |
| RAG (PyMuPDF, chunking, embeddings, Qdrant/Chroma) | Not started |
| React + TypeScript + Tailwind frontend | Not started — a plain HTML/CSS/JS dashboard was built instead (works with zero build step; a real React rewrite is a separate, larger task) |
| JWT auth, rate limiting, audit logs | Not started (CORS is currently wide open with `allow_origins=["*"]` — fine for a local demo, not for anything public) |
| Geospatial tools (OpenStreetMap/Overpass) | Not started |
| Memory / historical comparisons across runs | Not started (the new SQLite table is a prerequisite for this, but no comparison logic exists yet) |
| Cloud deployment | Not started |
| Hallucination/evaluation testing suite | Not started |

## How to run it

```bash
cd backend
python -m venv .venv
# Windows: .venv\Scripts\activate   |   Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then fill in your real TAVILY_API_KEY and GEMINI_API_KEY
uvicorn app.main:app --reload
```

Backend runs at `http://127.0.0.1:8000` (docs at `/docs`). Open the dashboard (the published link), point the "API Base" field at that address if it isn't already, and click **Check backend** to confirm it connects — then run an analysis from the form.

## Project structure

```
startup-intelligence/
├── README.md
├── .gitignore
├── frontend/
│   └── index.html            <- dashboard (just double-click to open in browser)
└── backend/
    ├── requirements.txt
    ├── .env.example          <- copy to .env and add your keys
    ├── startup_test.json     <- sample input
    └── app/
        ├── main.py           <- FastAPI app + endpoints
        ├── db.py             <- SQLite storage
        ├── models/startup.py <- Pydantic StartupInput
        ├── agents/           <- market, customer, competitor, location,
        │                        business_model, financial, risk, conflict,
        │                        sceptic, advisor, orchestrator
        └── tools/            <- web_research (Tavily), evidence, llm (Gemini)
```

Open `frontend/index.html` directly in your browser (no server needed) while the backend is running.

## Financial simulator (new)
- `backend/app/tools/finance.py` — deterministic break-even / runway maths (no LLM), 3 demand scenarios.
- `POST /finance/simulate` — validated by Pydantic (bad input -> 422).
- `backend/tests/test_finance.py` — run with `python -m pytest backend/tests` (11 tests).
- Dashboard page: **Financial Simulator**. Defaults are example values only; results are planning projections, not forecasts.

## Reliable analysis workflow (new)
- `POST /analyses` starts a background job and returns `job_id` (HTTP 202).
- `GET /analyses/{job_id}` returns live per-stage status (`pending/running/completed/failed`), duration and error for all 10 stages, plus `report_id` when done.
- One failing or slow agent (120 s timeout) no longer fails the whole analysis; it is marked `FAILED` and the rest of the report is still produced.
- Job status is held in memory (lost on restart); finished reports are saved in SQLite. `POST /startup` still works for older clients.
- Tests (17): `cd backend && python -m pytest tests`. They use fake agents, so no API keys or network are needed.

## Final advisor speed (fix)
- The Gemini prompt used to contain the *entire* analysis (all raw search results and evidence), making it huge and slow. It now sends a compact digest (capped at ~7,000 characters).
- Gemini is also capped by `LLM_TIMEOUT_SECONDS` (default 45, set in `.env`). On timeout the rule-based advisor report is shown instead of waiting.
- The server log prints `Final advisor LLM: N chars in prompt, X.Xs` so you can see where time goes.
