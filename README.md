# Portfolio Tracker

A small full-stack app for logging stock and crypto trades in **MongoDB**, then seeing holdings, totals, and charts. Live prices and history come from **Yahoo Finance** (via yfinance); the benchmark line is **SPY** as a stand-in for the S&P 500.

**Authors:** Akshay K, Arsen K, Stefan L · CS122

---

## What you get

- **Transactions:** buy/sell with ticker, quantity, price, date, optional memo (500 chars). Edit with PATCH, delete by id. Oversells are rejected.
- **Lists:** all rows newest first, filter by ticker, **Export CSV** in the browser or `GET /transactions/export`.
- **Demo:** button in the UI or `POST /demo/seed` replaces the whole collection with a fixed six-row sample.
- **Summary:** total value, cost basis, gain/loss, return %, per-asset rows, and **warnings** when a live quote fails (cost basis is used as a fallback).
- **Charts:** portfolio value over time, cumulative return vs SPY, and an allocation pie. Optional **from** / **to** query the API and refetch when you click **Apply** on the chart form.
- **Charts when Yahoo is thin:** if daily history is missing, the value chart falls back to a **flat line at your current portfolio total** (same idea as the summary cards). The benchmark then keeps the dates but sets the **SPY leg to 0%** until real SPY bars exist.
- **Sanity checks:** trade dates must sit between **1970-01-01** and **2100-12-31** (API + browser inputs).
- **Tests:** pytest with a fake in-memory collection and mocked prices—no Atlas required to run them.

Out of scope: logins, multi-user, tax lots, broker CSV import, dividends.

**Grading / demo:** walkthrough and screenshot filenames live in [`docs/DEMO.md`](docs/DEMO.md); drop PNGs under [`docs/screenshots/`](docs/screenshots/) when you have them.

---

## Stack

FastAPI, PyMongo, Pydantic, Pandas, yfinance, React 18, Vite, Recharts.

---

## Run it (two terminals)

**1. Backend** — Python 3.10+

```bash
cd backend
python -m venv venv
source venv/bin/activate    # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
```

Put your **`MONGO_URI`** in `backend/.env`. Optional: `MONGO_DB_NAME`, `FRONTEND_ORIGIN`, `SSL_CERT_FILE` if TLS complains on your machine.

```bash
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000` · Interactive docs: `/docs`

**2. Frontend** — Node 18+

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173`

If the API is not on port 8000, set **`VITE_API_BASE_URL`** in `frontend/.env` and restart Vite. The backend allows **both** `http://localhost:5173` and `http://127.0.0.1:5173` for local dev so either URL in the browser works with CORS.

---

## Tests and CI

Local:

```bash
cd backend && source venv/bin/activate && pytest
cd frontend && npm run build
```

GitHub **Actions** (see [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) runs the same pytest job and a production `npm run build` on push and pull request.

---

## API (short)

| Method | Path | Role |
| ------ | ---- | ---- |
| GET | `/health` | Liveness |
| POST | `/demo/seed` | Wipe `transactions`, insert demo set |
| POST | `/transactions` | Create buy/sell |
| GET | `/transactions` | List all, newest first |
| GET | `/transactions/export` | CSV download; optional `?ticker=` |
| GET | `/transactions/{ticker}` | One ticker |
| PATCH / DELETE | `/transactions/{id}` | `{id}` = Mongo ObjectId string |
| GET | `/holdings` | Holdings JSON |
| GET | `/portfolio` | Summary + assets + `warnings` |
| GET | `/performance` | Daily `{ date, portfolio_value }`; optional `from`, `to` (`YYYY-MM-DD`) |
| GET | `/benchmark` | Cumulative % vs SPY on the same dates |

Errors return JSON with `error`, `status_code`, and `detail`.

---

## Demo seed (what `/demo/seed` inserts)

| Ticker | Type | Qty | Price | Date | Memo |
| ------ | ---- | --- | ----- | ---- | ---- |
| AAPL | buy | 10 | 150 | 2024-01-10 | First tranche |
| AAPL | buy | 5 | 170 | 2024-03-15 | |
| MSFT | buy | 4 | 300 | 2024-02-20 | |
| TSLA | buy | 3 | 220 | 2024-04-05 | |
| BTC-USD | buy | 0.05 | 65000 | 2024-04-10 | |
| AAPL | sell | 2 | 190 | 2024-05-01 | |

---

## Environment

| Variable | Required | Default | Purpose |
| -------- | -------- | ------- | ------- |
| `MONGO_URI` | For a real DB | — | Mongo connection string |
| `MONGO_DB_NAME` | No | `portfolio_tracker` | Database name |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173` | CORS (comma-separated list allowed) |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Where the browser calls the API |

Server-side quote cache TTL is **60 seconds** to ease Yahoo rate limits.

---

## Troubleshooting

**MongoDB:** Atlas **Network Access** must allow your IP; user/password in the URI must match **Database Access**. The app loads **certifi** for TLS; set `SSL_CERT_FILE` if your machine needs a different CA bundle.

**“Could not load data: Failed to fetch”:** API not running, wrong `VITE_API_BASE_URL`, or browser blocked the call. Start `uvicorn`, match the URL to the port you use, restart `npm run dev` after editing `frontend/.env`, hard-refresh the tab.

**Charts flat or slow:** Yahoo throttling or gaps; wait and retry. Use **past** trade dates for the most reliable history. Clear the chart **From/To** fields and click **Apply** if you narrowed the window too far.
