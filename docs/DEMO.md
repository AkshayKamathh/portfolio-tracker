# Demo checklist (grading / presentation)

## Before you record or present

1. `backend/.env` has a valid `MONGO_URI`; Atlas allows your current IP.
2. Backend: `cd backend && source venv/bin/activate && uvicorn app.main:app --reload`
3. Frontend: `cd frontend && npm run dev` → open `http://localhost:5173`
4. Optional backup: screen record 60–90s of the flow below and keep it with your slides (not required in this repo).

## Suggested live order (~5 min)

1. **Load demo data** — confirm summary cards and charts populate (wait a few seconds if Yahoo is slow).
2. **Charts** — scroll through value, benchmark vs SPY, allocation; optionally set **From / To** and **Apply**.
3. **Holdings** — point out tickers and quantities.
4. **Transactions** — **Filter by ticker** (e.g. `AAPL`), **Export CSV**; open file briefly.
5. **Add / edit** — small buy or memo change, or show **oversell** rejection on a sell too large.
6. **API** — open `http://127.0.0.1:8000/docs`, try **GET /health** or **GET /portfolio**.
7. **Tests** — `cd backend && pytest` (no Atlas needed).

## Screenshots for the repo

Capture from your machine and save PNGs under [`screenshots/`](screenshots/). See that folder’s README for suggested file names. GitHub will render them if you link paths like `docs/screenshots/01-overview.png` from the main README after the files exist.
