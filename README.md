# Portfolio Tracker

A full-stack portfolio tracking dashboard for stocks and crypto. Built as a CS122 semester project.

## Team Members

- Akshay K
- Arsen K
- Stefan L

## Description

Portfolio Tracker lets a user record buy/sell transactions for stocks and crypto, stores them in MongoDB Atlas, and turns them into useful analytics: current holdings, weighted-average cost basis, live market value, gain/loss, historical portfolio value, and a head-to-head comparison against the S&P 500. The frontend is a clean React dashboard powered by Vite and Recharts.

## Quickstart (macOS)

### Prerequisites

- Python 3.10+
- Node.js + npm
- A MongoDB Atlas connection string (`MONGO_URI`)

Tip: point `core.excludesfile` at a global ignore file so editor cache folders under the repo never show up in `git status`.

### 1) Backend (FastAPI)

From the repo root:

```
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp ../.env.example .env
```

Edit `backend/.env` and set `MONGO_URI` to your Atlas URI (see `.env.example` for the format).

Start the API:

```
uvicorn app.main:app --reload
```

The API runs at `http://127.0.0.1:8000`. Docs are at `http://127.0.0.1:8000/docs`.

### 2) Frontend (Vite/React)

In a second terminal from the repo root:

```
cd frontend
npm install
npm run dev
```

Open the dashboard at `http://localhost:5173`.

## Verification checklist

### Backend health

```
curl http://127.0.0.1:8000/health
```

Expected:

```
{"status":"ok"}
```

### Seed demo data (optional, recommended for first run)

This resets the `transactions` collection and inserts the demo transactions listed below.

```
curl -X POST http://127.0.0.1:8000/demo/seed
```

Then refresh the dashboard. You should see populated holdings and charts.

## Features

- Add buy/sell transactions with ticker, quantity, price, date, and optional memo (up to 500 characters)
- Server-side oversell prevention (cannot sell more than you own)
- View all transactions, filter by ticker, edit or delete by id, export the current list as CSV
- Automatic holdings calculation with weighted-average buy price
- Live prices via `yfinance` (works for stocks like `AAPL` and crypto like `BTC-USD`)
- Portfolio summary: total value, cost basis, gain/loss, return %
- Historical portfolio value over time
- S&P 500 (SPY) benchmark comparison on cumulative return
- Asset allocation pie chart
- Polished dashboard UI with responsive grid, soft shadows, and green/red money colors
- PyTest suite that runs without a live MongoDB connection

## Tech Stack

| Layer    | Tools                                                              |
| -------- | ------------------------------------------------------------------ |
| Backend  | Python 3.10+, FastAPI, PyMongo, Pydantic v2, Pandas, yfinance      |
| Database | MongoDB Atlas                                                      |
| Frontend | React, Vite, Recharts, plain CSS                                   |
| Testing  | PyTest, FastAPI TestClient (with an in-memory fake collection)     |

## Folder Structure

```
portfolio-tracker/
  README.md
  .gitignore
  .env.example
  backend/
    requirements.txt
    pytest.ini
    app/
      __init__.py
      main.py
      config.py
      database.py
      models.py
      routes/
        __init__.py
        transactions.py
        portfolio.py
      services/
        __init__.py
        holdings.py
        prices.py
        performance.py
      utils/
        __init__.py
        serializers.py
    tests/
      conftest.py
      test_holdings.py
      test_transactions.py
      test_portfolio.py
  frontend/
    package.json
    index.html
    vite.config.js
    src/
      main.jsx
      App.jsx
      api.js
      styles.css
      components/
        TransactionForm.jsx
        SummaryCards.jsx
        Charts.jsx
        AssetTable.jsx
        TransactionTable.jsx
```

## Tests

The backend test suite runs without a live MongoDB connection (it uses an in-memory fake collection and monkeypatched price/history functions).

```
cd backend
source venv/bin/activate
pytest
```

## Environment Variables

| Variable             | Required          | Default                         | Notes                                                  |
| -------------------- | ----------------- | ------------------------------- | ------------------------------------------------------ |
| `MONGO_URI`          | Yes (real backend) | _empty_                        | MongoDB Atlas connection string                        |
| `MONGO_DB_NAME`      | No                | `portfolio_tracker`             | Database name                                          |
| `FRONTEND_ORIGIN`    | No                | `http://localhost:5173`         | Used for CORS allow-list                               |
| `VITE_API_BASE_URL`  | No                | `http://localhost:8000`         | URL the frontend uses to call the backend              |

`MONGO_URI` is the only secret you need. No paid stock API key is required because [`yfinance`](https://github.com/ranaroussi/yfinance) is used to pull prices from Yahoo Finance.

## Demo Data

Use these transactions to recreate the demo dataset:

| Ticker  | Type | Quantity | Price | Date       |
| ------- | ---- | -------- | ----- | ---------- |
| AAPL    | buy  | 10       | 150   | 2024-01-10 |
| AAPL    | buy  | 5        | 170   | 2024-03-15 |
| MSFT    | buy  | 4        | 300   | 2024-02-20 |
| TSLA    | buy  | 3        | 220   | 2024-04-05 |
| BTC-USD | buy  | 0.05     | 65000 | 2024-04-10 |
| AAPL    | sell | 2        | 190   | 2024-05-01 |

## API Endpoints

| Method | Path                       | Description                                            |
| ------ | -------------------------- | ------------------------------------------------------ |
| GET    | `/health`                  | Liveness check                                         |
| POST   | `/demo/seed`               | Clear DB + insert demo transactions                    |
| POST   | `/transactions`            | Create a buy or sell transaction                       |
| GET    | `/transactions`            | List all transactions, newest first                    |
| GET    | `/transactions/{ticker}`   | List transactions for one ticker                       |
| PATCH  | `/transactions/{id}`       | Update fields on a transaction (oversell rules apply)   |
| DELETE | `/transactions/{id}`       | Delete a transaction by Mongo ObjectId                 |
| GET    | `/holdings`                | Current per-ticker holdings derived from transactions  |
| GET    | `/portfolio`               | Full portfolio summary with live prices                |
| GET    | `/performance`             | Historical portfolio value over time                   |
| GET    | `/benchmark`               | Cumulative return vs S&P 500 (SPY)                     |

## Technical notes

- Single-user scope: no login or multi-user accounts.
- Backend tests use an in-memory `FakeCollection` plus `monkeypatch` instead of a live database.
- Price lookups use a 60-second in-memory cache to limit Yahoo Finance traffic.
- If a live quote is missing, `/portfolio` falls back to average buy price and adds a warning string to the JSON.
- Benchmark uses `SPY` as the S&P 500 proxy; switch to `^GSPC` in `app/services/performance.py` if you want the cash index.
- Holdings use weighted-average buy price only; realized gain on sells is not modeled separately.

## Troubleshooting (common setup issues)

### MongoDB Atlas connection errors

If endpoints like `/transactions` time out or return a Mongo connection error:

- Confirm your Atlas **Network Access** allows your current IP address.
- Confirm your Atlas **Database Access** user/password match your `MONGO_URI`.
- Ensure you replaced placeholders like `<password>` / angle brackets in the URI.

### yfinance / Yahoo Finance limitations

If charts look sparse or benchmark data is missing, it can be due to Yahoo Finance rate limiting or missing historical data for a ticker on certain dates. The backend is designed to return valid JSON and avoid crashing in these cases, but the chart may have fewer points.
