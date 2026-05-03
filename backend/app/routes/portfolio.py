"""HTTP endpoints for derived portfolio analytics."""

from datetime import date
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query

from app.database import get_transactions_collection
from app.services import prices
from app.services.holdings import calculate_holdings
from app.services.performance import compute_benchmark, compute_performance

router = APIRouter(tags=["portfolio"])


def _load_transactions() -> list[dict]:
    collection = get_transactions_collection()
    return list(collection.find({}))


@router.get("/holdings")
def get_holdings():
    return calculate_holdings(_load_transactions())


@router.get("/portfolio")
def get_portfolio():
    holdings = calculate_holdings(_load_transactions())
    assets: list[dict] = []
    warnings: list[str] = []
    total_value = 0.0
    total_cost = 0.0

    for h in holdings:
        ticker = h["ticker"]
        try:
            current_price = prices.get_current_price(ticker)
        except Exception as exc:
            current_price = h["avg_buy_price"]
            warnings.append(f"Could not fetch price for {ticker}: {exc}")

        market_value = h["quantity"] * current_price
        gain_loss = market_value - h["cost_basis"]
        return_percent = (
            (gain_loss / h["cost_basis"]) * 100 if h["cost_basis"] > 0 else 0.0
        )
        assets.append(
            {
                "ticker": ticker,
                "quantity": h["quantity"],
                "avg_buy_price": h["avg_buy_price"],
                "cost_basis": h["cost_basis"],
                "current_price": round(current_price, 2),
                "market_value": round(market_value, 2),
                "gain_loss": round(gain_loss, 2),
                "return_percent": round(return_percent, 2),
            }
        )
        total_value += market_value
        total_cost += h["cost_basis"]

    total_gain_loss = total_value - total_cost
    total_return_percent = (
        (total_gain_loss / total_cost) * 100 if total_cost > 0 else 0.0
    )

    return {
        "total_value": round(total_value, 2),
        "total_cost_basis": round(total_cost, 2),
        "total_gain_loss": round(total_gain_loss, 2),
        "total_return_percent": round(total_return_percent, 2),
        "assets": assets,
        "warnings": warnings,
    }


@router.get("/performance")
def get_performance(
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
):
    return compute_performance(
        _load_transactions(),
        from_date=from_date,
        to_date=to_date,
    )


@router.get("/benchmark")
def get_benchmark(
    from_date: Annotated[date | None, Query(alias="from")] = None,
    to_date: Annotated[date | None, Query(alias="to")] = None,
):
    performance = compute_performance(
        _load_transactions(),
        from_date=from_date,
        to_date=to_date,
    )
    return compute_benchmark(performance)


@router.get("/quotes")
def get_quotes(
    tickers: str = Query(
        ...,
        description="Comma-separated symbols, e.g. AAPL,MSFT,BTC-USD",
    ),
):
    """Batch latest prices (uses the same TTL cache as /portfolio)."""
    symbols = [t.strip().upper() for t in tickers.split(",") if t.strip()]
    if not symbols:
        raise HTTPException(status_code=422, detail="Provide at least one ticker.")

    prices_out: dict[str, float] = {}
    errors: list[str] = []
    for sym in symbols:
        try:
            prices_out[sym] = round(prices.get_current_price(sym), 4)
        except Exception as exc:
            errors.append(f"{sym}: {exc}")

    return {"prices": prices_out, "errors": errors}
