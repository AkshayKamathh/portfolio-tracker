"""Demo data seeding: reset transactions and insert the README demo rows."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter

from app.database import get_transactions_collection
from app.utils.serializers import serialize_transaction

router = APIRouter(prefix="/demo", tags=["demo"])


DEMO_TRANSACTIONS = [
    {"ticker": "AAPL", "transaction_type": "buy", "quantity": 10, "price": 150, "date": "2024-01-10"},
    {"ticker": "AAPL", "transaction_type": "buy", "quantity": 5, "price": 170, "date": "2024-03-15"},
    {"ticker": "MSFT", "transaction_type": "buy", "quantity": 4, "price": 300, "date": "2024-02-20"},
    {"ticker": "TSLA", "transaction_type": "buy", "quantity": 3, "price": 220, "date": "2024-04-05"},
    {"ticker": "BTC-USD", "transaction_type": "buy", "quantity": 0.05, "price": 65000, "date": "2024-04-10"},
    {"ticker": "AAPL", "transaction_type": "sell", "quantity": 2, "price": 190, "date": "2024-05-01"},
]


@router.post("/seed", status_code=201)
def seed_demo_transactions():
    collection = get_transactions_collection()
    collection.delete_many({})

    inserted = []
    for tx in DEMO_TRANSACTIONS:
        doc = {
            "ticker": tx["ticker"],
            "transaction_type": tx["transaction_type"],
            "quantity": float(tx["quantity"]),
            "price": float(tx["price"]),
            "date": tx["date"],
            "created_at": datetime.utcnow(),
        }
        result = collection.insert_one(doc)
        doc["_id"] = result.inserted_id
        inserted.append(serialize_transaction(doc))

    return {"message": "Demo data seeded", "count": len(inserted), "transactions": inserted}

