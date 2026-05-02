"""Pure functions that turn a list of transactions into current holdings."""

from datetime import date, datetime
from typing import Iterable


def _to_date(value) -> date:
    """Normalize a transaction date to a `datetime.date` for sorting."""
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value[:10]).date()
    return date.min


def _to_datetime(value) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime(value.year, value.month, value.day)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return datetime.min
    return datetime.min


def _sort_key(tx: dict):
    return (_to_date(tx.get("date")), _to_datetime(tx.get("created_at")))


def calculate_holdings(transactions: Iterable[dict]) -> list[dict]:
    """Return current holdings derived from a list of transactions.

    For each ticker we maintain a running quantity and a weighted-average buy
    price. Buys update both; sells reduce quantity but keep the average
    buy price the same (we do not track realized gains here).
    """
    sorted_tx = sorted(list(transactions), key=_sort_key)

    holdings: dict[str, dict] = {}
    for tx in sorted_tx:
        ticker = (tx.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        qty = float(tx.get("quantity", 0))
        price = float(tx.get("price", 0))
        ttype = tx.get("transaction_type")

        h = holdings.setdefault(
            ticker,
            {"ticker": ticker, "quantity": 0.0, "avg_buy_price": 0.0, "cost_basis": 0.0},
        )

        if ttype == "buy":
            new_qty = h["quantity"] + qty
            # Weighted average buy price: only buys contribute.
            total_cost = h["avg_buy_price"] * h["quantity"] + price * qty
            h["avg_buy_price"] = total_cost / new_qty if new_qty > 0 else 0.0
            h["quantity"] = new_qty
        elif ttype == "sell":
            if qty > h["quantity"] + 1e-9:
                raise ValueError(
                    f"Cannot sell {qty} of {ticker}: only {h['quantity']} owned"
                )
            h["quantity"] -= qty
        else:
            raise ValueError(f"Unknown transaction_type: {ttype}")

        h["cost_basis"] = h["quantity"] * h["avg_buy_price"]

    result = []
    for h in holdings.values():
        if h["quantity"] <= 1e-9:
            continue
        result.append(
            {
                "ticker": h["ticker"],
                "quantity": round(h["quantity"], 8),
                "avg_buy_price": round(h["avg_buy_price"], 2),
                "cost_basis": round(h["cost_basis"], 2),
            }
        )
    result.sort(key=lambda r: r["ticker"])
    return result


def current_quantity(transactions: Iterable[dict], ticker: str) -> float:
    """How many units of `ticker` are currently held."""
    target = (ticker or "").strip().upper()
    for h in calculate_holdings(transactions):
        if h["ticker"] == target:
            return h["quantity"]
    return 0.0
