# Portfolio Tracker

CS122 semester project — full-stack app to log stock/crypto trades, persist them in MongoDB Atlas, and visualize portfolio value, holdings, and a benchmark vs the S&P 500 (via SPY).

**Team:** Akshay K, Arsen K, Stefan L

---

## What it does today

| Layer | Behavior |
| ----- | -------- |
| **Transactions** | Create buy/sell with ticker, quantity, price, date, optional **memo** (500 chars max). **Edit** (PATCH) and **delete** by MongoDB id. **Oversell** blocked on create and on edit (full ledger re-checked). |
| **Lists** | All transactions sorted newest first; **filter by ticker**; optional **CSV export** of whatever is on screen (includes memo). |
| **Demo** | **Load demo data** in the UI or `POST /demo/seed` — wipes the `transactions` collection and inserts six fixed rows (see table below). First AAPL buy includes a sample memo. |
| **Analytics** | **Holdings:** quantity, weighted-average buy price, cost basis. **Portfolio:** live prices via **yfinance**, market value, gain/loss, return %; **warnings** if a quote fails (falls back to avg buy). **Performance:** daily portfolio value from history. **Benchmark:** cumulative % vs SPY on the same dates. **Charts:** value over time, benchmark lines, allocation pie. |
| **Quality** | **PyTest** with an in-memory fake Mongo collection and mocked prices — **no Atlas required** to run tests. |

**Out of scope:** logins, multi-user, tax lots, broker CSV import, dividends/cash ledger.

---

## Try it in five minutes (self-serve)

1. Follow **Setup** below until the API and Vite app both run.
2. Open `http://localhost:5173` → click **Load demo data** → confirm summary, charts, and holdings populate.
3. Use **Filter by ticker** (e.g. `AAPL`) → **Export CSV** → open the file in Excel or Numbers.
4. Add a small **buy**, then a **sell** below your position — confirm oversell is rejected.
5. Optional: open `http://127.0.0.1:8000/docs` and call the same endpoints with **Try it out**.

---

## Stack

| Layer | Tools |
| ----- | ----- |
| Backend | Python 3.10+, FastAPI, Pydantic v2, PyMongo, Pandas, yfinance |
| Database | MongoDB Atlas (`MONGO_URI`) |
| Frontend | React 18, Vite, Recharts, plain CSS |
| Tests | PyTest, Starlette `TestClient`, in-memory `FakeCollection` |

---

## Setup (macOS)

**Prerequisites:** Python 3.10+, Node 18+, MongoDB Atlas URI.

**Backend**

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
```

Edit `backend/.env`: set **`MONGO_URI`** (see `.env.example`). Optional: `MONGO_DB_NAME`, `FRONTEND_ORIGIN`, or `SSL_CERT_FILE` if TLS issues on your machine.

```bash
uvicorn app.main:app --reload
```

API: `http://127.0.0.1:8000` — interactive docs: `/docs`.

**Frontend** (second terminal)

```bash
cd frontend
npm install
npm run dev
```

App: `http://localhost:5173` — set **`VITE_API_BASE_URL`** in `frontend/.env` if the API is not on port 8000.

---

## Quick checks

```bash
curl http://127.0.0.1:8000/health
# → {"status":"ok"}

curl -X POST http://127.0.0.1:8000/demo/seed
# → seeds demo rows (clears existing transactions first)
```

**Tests** (no live MongoDB):

```bash
cd backend && source venv/bin/activate && pytest
```

**Frontend build:**

```bash
cd frontend && npm run build
```

---

## API (summary)

| Method | Path | Purpose |
| ------ | ---- | ------- |
| GET | `/health` | Liveness |
| POST | `/demo/seed` | Delete all transactions, insert demo set |
| POST | `/transactions` | Create buy/sell |
| GET | `/transactions` | List all (newest first) |
| GET | `/transactions/export` | CSV download; optional query `ticker` |
| GET | `/transactions/{ticker}` | List for one ticker (uppercased) |
| PATCH | `/transactions/{id}` | Partial update; `{id}` = Mongo ObjectId |
| DELETE | `/transactions/{id}` | Delete by ObjectId |
| GET | `/holdings` | Holdings JSON only (same math as portfolio; UI uses `/portfolio`) |
| GET | `/portfolio` | Summary + per-asset rows + `warnings` |
| GET | `/performance` | `[{ date, portfolio_value }, ...]` |
| GET | `/benchmark` | `[{ date, portfolio_return, benchmark_return }, ...]` |

Errors return JSON: `error`, `status_code`, `detail`.

---

## Demo seed rows

`POST /demo/seed` replaces **all** documents in `transactions` with:

| Ticker | Type | Qty | Price | Date | Memo (if any) |
| ------ | ---- | --- | ----- | ---- | ------------- |
| AAPL | buy | 10 | 150 | 2024-01-10 | First tranche |
| AAPL | buy | 5 | 170 | 2024-03-15 | |
| MSFT | buy | 4 | 300 | 2024-02-20 | |
| TSLA | buy | 3 | 220 | 2024-04-05 | |
| BTC-USD | buy | 0.05 | 65000 | 2024-04-10 | |
| AAPL | sell | 2 | 190 | 2024-05-01 | |

---

## Environment

| Variable | Required for real API | Default | Notes |
| -------- | --------------------- | ------- | ----- |
| `MONGO_URI` | Yes | — | Atlas connection string |
| `MONGO_DB_NAME` | No | `portfolio_tracker` | Database name |
| `FRONTEND_ORIGIN` | No | `http://localhost:5173` | CORS |
| `VITE_API_BASE_URL` | No | `http://localhost:8000` | Frontend → API |

Prices come from **Yahoo Finance via yfinance** (no paid market data key). The backend caches quotes for **60 seconds** to reduce rate limits.

---

## Repo layout (main paths)

```
backend/app/
  main.py              # CORS, routers, exception handlers
  config.py            # env
  database.py          # Mongo client (lazy), certifi TLS
  models.py            # Pydantic request/response models
  routes/
    transactions.py    # CRUD + PATCH
    portfolio.py       # holdings, portfolio, performance, benchmark
    demo.py            # /demo/seed
  services/
    holdings.py        # weighted avg cost, qty
    prices.py          # yfinance + TTL cache
    performance.py     # history + SPY benchmark
  utils/serializers.py
backend/tests/         # conftest FakeCollection + route tests
frontend/src/
  App.jsx
  api.js
  components/          # form, tables, charts, summary cards
  utils/exportTransactionsCsv.js
```

---

## Behavior and limits

- **Single user:** no auth; one global transaction list.
- **Holdings:** weighted-average buy price; sells reduce shares only (no separate realized gain line item).
- **Benchmark:** **SPY** only in code (`performance.py`); change ticker there if you want another proxy.
- **yfinance:** throttling or gaps can shorten charts; `/portfolio` still returns JSON and may include **warnings**.

---

## Troubleshooting

**MongoDB:** Atlas **Network Access** must allow your IP; **Database Access** user/password must match `MONGO_URI`; replace placeholders like `<password>` in the URI. TLS: backend uses **certifi** by default; override with `SSL_CERT_FILE` if needed.

**Charts empty or sparse:** Yahoo data or rate limits; try again after a minute or use fewer tickers.
