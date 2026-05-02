"""Route-level tests for the portfolio analytics endpoints."""

import pandas as pd

from app.routes import portfolio as portfolio_routes
from app.services import performance as performance_service


def _create_buy(client, ticker, quantity, price, date):
    return client.post(
        "/transactions",
        json={
            "ticker": ticker,
            "transaction_type": "buy",
            "quantity": quantity,
            "price": price,
            "date": date,
        },
    )


def test_empty_portfolio_returns_zeros(client):
    response = client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert data["total_value"] == 0
    assert data["total_cost_basis"] == 0
    assert data["total_gain_loss"] == 0
    assert data["total_return_percent"] == 0
    assert data["assets"] == []


def test_holdings_endpoint(client):
    _create_buy(client, "AAPL", 10, 100, "2024-01-10")
    _create_buy(client, "AAPL", 5, 120, "2024-03-15")
    response = client.get("/holdings")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "AAPL"
    assert data[0]["quantity"] == 15
    assert data[0]["avg_buy_price"] == 106.67


def test_portfolio_summary_math_with_mocked_prices(client, monkeypatch):
    _create_buy(client, "AAPL", 10, 100, "2024-01-10")
    _create_buy(client, "MSFT", 4, 300, "2024-02-20")

    fake_prices = {"AAPL": 150.0, "MSFT": 350.0}
    monkeypatch.setattr(
        portfolio_routes.prices,
        "get_current_price",
        lambda ticker: fake_prices[ticker],
    )

    response = client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()

    assets = {a["ticker"]: a for a in data["assets"]}
    aapl = assets["AAPL"]
    msft = assets["MSFT"]

    assert aapl["market_value"] == 1500.0
    assert aapl["gain_loss"] == 500.0
    assert aapl["return_percent"] == 50.0

    assert msft["market_value"] == 1400.0
    assert msft["gain_loss"] == 200.0
    assert round(msft["return_percent"], 2) == 16.67

    assert data["total_value"] == 2900.0
    assert data["total_cost_basis"] == 2200.0
    assert data["total_gain_loss"] == 700.0
    assert round(data["total_return_percent"], 2) == 31.82


def test_portfolio_handles_price_failure(client, monkeypatch):
    _create_buy(client, "AAPL", 10, 100, "2024-01-10")

    def boom(ticker):
        raise ValueError("yfinance offline")

    monkeypatch.setattr(portfolio_routes.prices, "get_current_price", boom)

    response = client.get("/portfolio")
    assert response.status_code == 200
    data = response.json()
    assert len(data["warnings"]) == 1
    aapl = data["assets"][0]
    assert aapl["current_price"] == 100.0
    assert aapl["market_value"] == 1000.0
    assert aapl["gain_loss"] == 0.0


def test_performance_uses_historical_close(client, monkeypatch):
    _create_buy(client, "AAPL", 10, 100, "2024-01-10")

    def fake_history(ticker, start, end):
        idx = pd.Index(["2024-01-10", "2024-01-11", "2024-01-12"])
        return pd.Series([100.0, 110.0, 120.0], index=idx, name=ticker)

    monkeypatch.setattr(
        performance_service.prices, "get_historical_close", fake_history
    )

    response = client.get("/performance")
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"date": "2024-01-10", "portfolio_value": 1000.0},
        {"date": "2024-01-11", "portfolio_value": 1100.0},
        {"date": "2024-01-12", "portfolio_value": 1200.0},
    ]


def test_performance_empty_when_no_transactions(client):
    response = client.get("/performance")
    assert response.status_code == 200
    assert response.json() == []


def test_benchmark_aligns_portfolio_and_spy(client, monkeypatch):
    _create_buy(client, "AAPL", 10, 100, "2024-01-10")

    def fake_history(ticker, start, end):
        idx = pd.Index(["2024-01-10", "2024-01-11", "2024-01-12"])
        if ticker == "AAPL":
            return pd.Series([100.0, 110.0, 120.0], index=idx, name="AAPL")
        if ticker == "SPY":
            return pd.Series([400.0, 404.0, 408.0], index=idx, name="SPY")
        raise ValueError(f"unexpected ticker {ticker}")

    monkeypatch.setattr(
        performance_service.prices, "get_historical_close", fake_history
    )

    response = client.get("/benchmark")
    assert response.status_code == 200
    data = response.json()
    assert data[0] == {
        "date": "2024-01-10",
        "portfolio_return": 0.0,
        "benchmark_return": 0.0,
    }
    assert data[-1]["portfolio_return"] == 20.0
    assert data[-1]["benchmark_return"] == 2.0


def test_benchmark_empty_when_no_transactions(client):
    response = client.get("/benchmark")
    assert response.status_code == 200
    assert response.json() == []
