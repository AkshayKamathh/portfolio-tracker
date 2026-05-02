"""Transaction CRUD and CSV export."""

from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response

from app.database import get_transactions_collection
from app.models import TransactionCreate, TransactionUpdate
from app.services.holdings import calculate_holdings, current_quantity
from app.utils.serializers import serialize_transaction
from app.utils.transaction_csv import transactions_csv_bytes

router = APIRouter(prefix="/transactions", tags=["transactions"])


@router.post("", status_code=201)
def create_transaction(payload: TransactionCreate):
    collection = get_transactions_collection()

    if payload.transaction_type == "sell":
        existing = list(collection.find({"ticker": payload.ticker}))
        owned = current_quantity(existing, payload.ticker)
        if payload.quantity > owned + 1e-9:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Cannot sell {payload.quantity} of {payload.ticker}: "
                    f"only {owned} owned"
                ),
            )

    doc = {
        "ticker": payload.ticker,
        "transaction_type": payload.transaction_type,
        "quantity": float(payload.quantity),
        "price": float(payload.price),
        "date": payload.date.isoformat(),
        "created_at": datetime.utcnow(),
    }
    if payload.memo:
        doc["memo"] = payload.memo
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_transaction(doc)


@router.get("")
def list_transactions():
    collection = get_transactions_collection()
    return [
        serialize_transaction(doc)
        for doc in collection.find({}).sort([("date", -1), ("created_at", -1)])
    ]


@router.get("/export")
def export_transactions_csv(ticker: str | None = Query(None, description="Optional ticker filter")):
    collection = get_transactions_collection()
    symbol = (ticker or "").strip().upper() or None
    query = {"ticker": symbol} if symbol else {}
    docs = collection.find(query).sort([("date", -1), ("created_at", -1)])
    rows = [serialize_transaction(doc) for doc in docs]
    body, filename = transactions_csv_bytes(rows, ticker_filter=symbol)
    return Response(
        content=body,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/{ticker}")
def list_transactions_by_ticker(ticker: str):
    collection = get_transactions_collection()
    symbol = (ticker or "").strip().upper()
    return [
        serialize_transaction(doc)
        for doc in collection.find({"ticker": symbol}).sort(
            [("date", -1), ("created_at", -1)]
        )
    ]


def _merge_transaction_update(existing: dict, patch: dict) -> dict:
    merged = dict(existing)
    if "ticker" in patch:
        merged["ticker"] = patch["ticker"]
    if "transaction_type" in patch:
        merged["transaction_type"] = patch["transaction_type"]
    if "quantity" in patch:
        merged["quantity"] = float(patch["quantity"])
    if "price" in patch:
        merged["price"] = float(patch["price"])
    if "date" in patch:
        d = patch["date"]
        merged["date"] = d.isoformat() if hasattr(d, "isoformat") else d
    if "memo" in patch:
        merged["memo"] = patch["memo"] or ""
    return merged


@router.patch("/{transaction_id}")
def update_transaction(transaction_id: str, payload: TransactionUpdate):
    collection = get_transactions_collection()
    try:
        oid = ObjectId(transaction_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Transaction not found")

    existing = collection.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    merged = _merge_transaction_update(existing, updates)
    all_docs = list(collection.find({}))
    others = [d for d in all_docs if d["_id"] != oid]
    try:
        calculate_holdings(others + [merged])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    set_fields: dict = {}
    if "ticker" in updates:
        set_fields["ticker"] = merged["ticker"]
    if "transaction_type" in updates:
        set_fields["transaction_type"] = merged["transaction_type"]
    if "quantity" in updates:
        set_fields["quantity"] = merged["quantity"]
    if "price" in updates:
        set_fields["price"] = merged["price"]
    if "date" in updates:
        set_fields["date"] = merged["date"]
    if "memo" in updates:
        set_fields["memo"] = merged.get("memo", "")

    collection.update_one({"_id": oid}, {"$set": set_fields})
    updated = collection.find_one({"_id": oid})
    return serialize_transaction(updated)


@router.delete("/{transaction_id}")
def delete_transaction(transaction_id: str):
    collection = get_transactions_collection()
    try:
        oid = ObjectId(transaction_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Transaction not found")

    result = collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted"}
