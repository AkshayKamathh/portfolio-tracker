"""Alert /check endpoint that evaluates current prices."""

from datetime import datetime

from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, HTTPException

from app.database import get_alerts_collection
from app.models import AlertCreate, AlertUpdate
from app.services import prices
from app.utils.serializers import serialize_alert

router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("", status_code=201)
def create_alert(payload: AlertCreate):
    """Create a new alert. Starts active=True, untriggered."""
    collection = get_alerts_collection()
    doc = {
        "ticker": payload.ticker,
        "direction": payload.direction,
        "threshold": float(payload.threshold),
        "active": True,
        "created_at": datetime.utcnow(),
        "triggered_at": None,
        "note": payload.note,
    }
    result = collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return serialize_alert(doc)


@router.get("")
def list_alerts():
    """All alerts, newest first."""
    collection = get_alerts_collection()
    return [
        serialize_alert(doc)
        for doc in collection.find({}).sort("created_at", -1)
    ]


# /check must be declared BEFORE /{alert_id} or FastAPI tries to match
# "check" as an alert_id and crashes. Path-parameter routes are greedy.
@router.get("/check")
def check_alerts():
    """Evaluate active alerts against current prices.
    Returns the list of newly-triggered alerts so the UI can show a banner."""
    collection = get_alerts_collection()
    active = list(collection.find({"active": True}))
    if not active:
        return {"triggered": []}

    # Deduplicate tickers — if user has 5 alerts on AAPL we only fetch once.
    tickers = sorted({doc["ticker"] for doc in active})

    # Per-ticker fetch — same error-tolerant pattern as /quotes in portfolio.py.
    # If Yahoo fails for one ticker, skip its alerts this round rather than
    # crashing the whole /check call.
    quotes: dict[str, float] = {}
    for sym in tickers:
        try:
            quotes[sym] = prices.get_current_price(sym)
        except Exception:
            continue

    triggered = []
    now = datetime.utcnow()

    for doc in active:
        price = quotes.get(doc["ticker"])
        if price is None:
            continue  # quote failed — try again next /check

        fired = (
            (doc["direction"] == "below" and price <= doc["threshold"])
            or (doc["direction"] == "above" and price >= doc["threshold"])
        )
        if fired:
            collection.update_one(
                {"_id": doc["_id"]},
                {"$set": {"active": False, "triggered_at": now}},
            )
            doc["active"] = False
            doc["triggered_at"] = now
            serialized = serialize_alert(doc)
            serialized["triggered_price"] = round(price, 2)
            triggered.append(serialized)

    return {"triggered": triggered}


@router.patch("/{alert_id}")
def update_alert(alert_id: str, payload: AlertUpdate):
    """Edit any subset of fields. Common use: re-enable a triggered alert
    by sending {"active": true}, or move the threshold."""
    collection = get_alerts_collection()
    try:
        oid = ObjectId(alert_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Alert not found")

    existing = collection.find_one({"_id": oid})
    if existing is None:
        raise HTTPException(status_code=404, detail="Alert not found")

    # exclude_unset=True → only fields the user actually sent.
    # Same trick transactions.py uses for partial updates.
    updates = payload.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="No fields to update")

    # Re-activating a triggered alert clears its old timestamp so it can fire again.
    if updates.get("active") is True:
        updates["triggered_at"] = None

    collection.update_one({"_id": oid}, {"$set": updates})
    return serialize_alert(collection.find_one({"_id": oid}))


@router.delete("/{alert_id}")
def delete_alert(alert_id: str):
    collection = get_alerts_collection()
    try:
        oid = ObjectId(alert_id)
    except (InvalidId, TypeError):
        raise HTTPException(status_code=404, detail="Alert not found")

    result = collection.delete_one({"_id": oid})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"message": "Alert deleted"}