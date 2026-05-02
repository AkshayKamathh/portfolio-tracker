"""Unit tests for the pure holdings calculation."""

from datetime import datetime

import pytest

from app.services.holdings import calculate_holdings, current_quantity


def _tx(ticker, ttype, qty, price, date_str, created_at=None):
    return {
        "ticker": ticker,
        "transaction_type": ttype,
        "quantity": qty,
        "price": price,
        "date": date_str,
        "created_at": created_at or datetime.fromisoformat(date_str + "T00:00:00"),
    }


def test_weighted_average_buy_price():
    transactions = [
        _tx("AAPL", "buy", 10, 100, "2024-01-10"),
        _tx("AAPL", "buy", 5, 120, "2024-03-15"),
    ]
    holdings = calculate_holdings(transactions)
    assert len(holdings) == 1
    aapl = holdings[0]
    assert aapl["ticker"] == "AAPL"
    assert aapl["quantity"] == 15
    assert aapl["avg_buy_price"] == 106.67
    assert aapl["cost_basis"] == 1600.0


def test_sell_reduces_quantity_and_keeps_avg():
    transactions = [
        _tx("AAPL", "buy", 10, 100, "2024-01-10"),
        _tx("AAPL", "buy", 5, 120, "2024-03-15"),
        _tx("AAPL", "sell", 3, 130, "2024-05-01"),
    ]
    holdings = calculate_holdings(transactions)
    aapl = holdings[0]
    assert aapl["quantity"] == 12
    assert aapl["avg_buy_price"] == 106.67


def test_zero_quantity_holdings_removed():
    transactions = [
        _tx("MSFT", "buy", 4, 300, "2024-02-20"),
        _tx("MSFT", "sell", 4, 350, "2024-04-01"),
    ]
    holdings = calculate_holdings(transactions)
    assert holdings == []


def test_oversell_raises_value_error():
    transactions = [
        _tx("TSLA", "buy", 3, 220, "2024-04-05"),
        _tx("TSLA", "sell", 5, 230, "2024-04-10"),
    ]
    with pytest.raises(ValueError):
        calculate_holdings(transactions)


def test_current_quantity_helper():
    transactions = [
        _tx("AAPL", "buy", 10, 100, "2024-01-10"),
        _tx("AAPL", "sell", 4, 150, "2024-02-10"),
    ]
    assert current_quantity(transactions, "aapl") == 6
    assert current_quantity(transactions, "MSFT") == 0


def test_crypto_fractional_quantity():
    transactions = [
        _tx("BTC-USD", "buy", 0.05, 65000, "2024-04-10"),
        _tx("BTC-USD", "buy", 0.025, 67000, "2024-04-20"),
    ]
    holdings = calculate_holdings(transactions)
    btc = holdings[0]
    assert btc["ticker"] == "BTC-USD"
    assert btc["quantity"] == 0.075
    expected_avg = round((0.05 * 65000 + 0.025 * 67000) / 0.075, 2)
    assert btc["avg_buy_price"] == expected_avg
