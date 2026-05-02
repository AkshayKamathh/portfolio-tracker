"""Tests for the demo data seeding endpoint."""


def test_seed_demo_is_deterministic_and_clears_existing(client, fake_collection):
    # Insert a non-demo transaction to ensure it gets cleared.
    fake_collection.insert_one(
        {
            "ticker": "SHOULD-CLEAR",
            "transaction_type": "buy",
            "quantity": 1.0,
            "price": 123.0,
            "date": "2024-01-01",
            "created_at": __import__("datetime").datetime.utcnow(),
        }
    )

    response = client.post("/demo/seed")
    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Demo data seeded"
    assert data["count"] == 6

    txs = client.get("/transactions").json()
    assert len(txs) == 6

    tickers = {tx["ticker"] for tx in txs}
    assert tickers == {"AAPL", "MSFT", "TSLA", "BTC-USD"}
    assert "SHOULD-CLEAR" not in tickers


def test_seed_demo_holdings_math(client):
    # Seed once, then validate derived holdings math.
    client.post("/demo/seed")

    holdings = client.get("/holdings").json()
    by_ticker = {h["ticker"]: h for h in holdings}

    # AAPL: buys 10@150 + 5@170 => avg_buy = 2350/15 = 156.666... => 156.67
    # Then sell 2 => quantity = 15 - 2 = 13
    # cost_basis = 13 * 156.666... = 2036.66... => 2036.67
    assert by_ticker["AAPL"]["quantity"] == 13.0
    assert by_ticker["AAPL"]["avg_buy_price"] == 156.67
    assert by_ticker["AAPL"]["cost_basis"] == 2036.67

    assert by_ticker["MSFT"]["quantity"] == 4.0
    assert by_ticker["MSFT"]["avg_buy_price"] == 300.0
    assert by_ticker["MSFT"]["cost_basis"] == 1200.0

    assert by_ticker["TSLA"]["quantity"] == 3.0
    assert by_ticker["TSLA"]["avg_buy_price"] == 220.0
    assert by_ticker["TSLA"]["cost_basis"] == 660.0

    assert by_ticker["BTC-USD"]["quantity"] == 0.05
    assert by_ticker["BTC-USD"]["avg_buy_price"] == 65000.0
    assert by_ticker["BTC-USD"]["cost_basis"] == 3250.0

