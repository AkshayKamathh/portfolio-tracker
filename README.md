# Portfolio Tracker

Log stock and crypto trades, store them in MongoDB, and view holdings, portfolio value, and a simple benchmark against the S&P 500 (via SPY and Yahoo Finance).

**Authors:** Akshay K, Arsen K, Stefan L · CS122

---

## Features

- Buy/sell with ticker, quantity, price, date, optional memo; edit (PATCH) and delete by id; oversell blocked.
- List all transactions or filter by ticker; export the current list as CSV (browser or `GET /transactions/export`).
- Demo seed from the UI or `POST /demo/seed` (replaces all rows with a fixed sample set).
- Summary cards, charts (value over time, vs SPY, allocation), optional **from** / **to** dates on performance and benchmark.
- Backend tests use an in-memory fake collection and mocked prices (no Atlas required).

Not included: auth, multi-user, tax lots, broker CSV import, dividends.

**Demo for graders:** step-by-step flow and screenshot checklist → [`docs/DEMO.md`](docs/DEMO.md). Drop PNGs into [`docs/screenshots/`](docs/screenshots/) after you capture them locally.

---

## Stack

FastAPI · PyMongo · Pydantic · Pandas · yfinance · React 18 · Vite · Recharts

---

## Run it locally

**Backend** (Python 3.10+)

```bash
cd backend
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example .env
```

Set `MONGO_URI` in `backend/.env` (see `.env.example`). Optional: `MONGO_DB_NAME`, `FRONTEND_ORIGIN`, `SSL_CERT_FILE` if TLS fails on your machine.

```bash
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000` · OpenAPI: `/docs`

**Frontend** (Node 18+)

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173` · If the API is not on port 8000, set `VITE_API_BASE_URL` in `frontend/.env`.

---

## Tests and production build

```bash
cd backend && source venv/bin/activate && pytest
cd frontend && npm run build
```

---

## API (summary)

| Method | Path | Notes |
| ------ | ---- | ----- |
| GET | `/health` | Liveness |
| POST | `/demo/seed` | Wipes `transactions`, inserts demo rows |
| POST | `/transactions` | Create buy/sell |
| GET | `/transactions` | Newest first |
| GET | `/transactions/export` | CSV; optional `?ticker=` |
| GET | `/transactions/{ticker}` | One ticker |
| PATCH / DELETE | `/transactions/{id}` | `{id}` = ObjectId string |
| GET | `/holdings` | Holdings JSON |
| GET | `/portfolio` | Summary + assets + `warnings` |
| GET | `/performance` | Daily value; optional `from`, `to` (`YYYY-MM-DD`) |
| GET | `/benchmark` | Cumulative % vs SPY; same date range |

Errors return JSON with `error`, `status_code`, and `detail`.

---

## Demo seed rows

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

| Variable | Required | Default | Role |
| -------- | -------- | ------- | ---- |
| `MONGO_URI` | For real DB | — | Mongo connection string |
| `MONGO_DB_NAME` | No | `portfolio_tracker` | Database name |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173` | CORS |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Frontend → API |

Quotes are cached for 60 seconds on the server to ease rate limits.

---

## Behavior notes

- Single global ledger (no login).
- Holdings use weighted-average buy price; sells reduce shares only.
- Benchmark ticker is **SPY** in code; swap there if you want another index fund.
- Yahoo data can be sparse or slow; the API still returns JSON and may add **warnings** when a live quote fails.
- **Performance / benchmark** charts use a window through the **latest transaction date**, even if that date is still in the future, so the lines are not empty when all trades are dated “tomorrow.” Yahoo may still omit prices for true future calendar days until the market prints a bar.

---

## Troubleshooting

**MongoDB:** Allow your IP in Atlas **Network Access**; check user/password in `MONGO_URI`. The backend uses **certifi** for TLS; set `SSL_CERT_FILE` if your environment needs a different CA bundle.

**Charts:** If history is empty, wait and retry or reduce tickers; Yahoo throttling happens sometimes.
