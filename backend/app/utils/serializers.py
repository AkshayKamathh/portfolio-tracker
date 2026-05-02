"""Helpers for converting MongoDB documents into JSON-friendly dicts."""

from datetime import date, datetime
from typing import Any


def _stringify(value: Any) -> Any:
    if isinstance(value, datetime):
        return value.isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return value


def serialize_transaction(doc: dict) -> dict:
    """Convert a transaction document into an API-safe dict."""
    if doc is None:
        return {}
    return {
        "id": str(doc["_id"]),
        "ticker": doc.get("ticker", ""),
        "transaction_type": doc.get("transaction_type", ""),
        "quantity": float(doc.get("quantity", 0)),
        "price": float(doc.get("price", 0)),
        "date": _stringify(doc.get("date", "")) or "",
        "created_at": _stringify(doc.get("created_at", "")) or "",
    }
