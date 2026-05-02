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
    """Mongo transaction doc → JSON field names and string ids."""
    if doc is None:
        return {}
    raw_memo = doc.get("memo", "")
    memo = raw_memo.strip() if isinstance(raw_memo, str) else ""
    return {
        "id": str(doc["_id"]),
        "ticker": doc.get("ticker", ""),
        "transaction_type": doc.get("transaction_type", ""),
        "quantity": float(doc.get("quantity", 0)),
        "price": float(doc.get("price", 0)),
        "date": _stringify(doc.get("date", "")) or "",
        "memo": memo,
        "created_at": _stringify(doc.get("created_at", "")) or "",
    }

def serialize_alert(doc: dict) -> dict:
    """Convert a Mongo alert doc to a JSON-friendly dict.
    Mirrors serialize_transaction: _id (ObjectId) -> id (str)."""
    return {
        "id": str(doc["_id"]),
        "ticker": doc["ticker"],
        "direction": doc["direction"],
        "threshold": doc["threshold"],
        "active": doc["active"],
        "created_at": (
            doc["created_at"].isoformat()
            if hasattr(doc.get("created_at"), "isoformat")
            else doc.get("created_at")
        ),
        "triggered_at": (
            doc["triggered_at"].isoformat()
            if hasattr(doc.get("triggered_at"), "isoformat")
            else doc.get("triggered_at")
        ),
        "note": doc.get("note"),
    }