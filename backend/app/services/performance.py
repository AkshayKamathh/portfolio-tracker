"""Historical portfolio performance and S&P 500 benchmark comparison."""

from datetime import date, datetime, timedelta
from typing import Iterable

import pandas as pd

from app.services import prices
from app.services.holdings import _to_date, _sort_key


def _earliest_date(transactions: list[dict]) -> date | None:
    if not transactions:
        return None
    return min(_to_date(tx.get("date")) for tx in transactions)


def _quantity_timeline(transactions: list[dict]) -> dict[str, list[tuple[date, float]]]:
    """Per-ticker list of (date, cumulative_quantity) after each transaction."""
    sorted_tx = sorted(transactions, key=_sort_key)
    running: dict[str, float] = {}
    timeline: dict[str, list[tuple[date, float]]] = {}

    for tx in sorted_tx:
        ticker = (tx.get("ticker") or "").strip().upper()
        if not ticker:
            continue
        qty = float(tx.get("quantity", 0))
        ttype = tx.get("transaction_type")
        d = _to_date(tx.get("date"))

        current = running.get(ticker, 0.0)
        if ttype == "buy":
            current += qty
        elif ttype == "sell":
            current = max(0.0, current - qty)
        running[ticker] = current
        timeline.setdefault(ticker, []).append((d, current))

    return timeline


def _quantity_on(timeline: list[tuple[date, float]], target: date) -> float:
    """How many units were owned on `target` given the per-ticker timeline."""
    qty = 0.0
    for d, q in timeline:
        if d <= target:
            qty = q
        else:
            break
    return qty


def compute_performance(
    transactions: Iterable[dict],
    *,
    from_date: date | None = None,
    to_date: date | None = None,
) -> list[dict]:
    """Return a list of {date, portfolio_value} points across the portfolio history."""
    tx_list = list(transactions)
    if not tx_list:
        return []

    earliest = _earliest_date(tx_list)
    if earliest is None:
        return []
    today = date.today()
    window_start = max(earliest, from_date) if from_date else earliest
    window_end = min(today, to_date) if to_date else today
    if window_end < window_start:
        return []

    timelines = _quantity_timeline(tx_list)
    start_str = window_start.isoformat()
    # yfinance end date is exclusive; add a day so today is included.
    end_str = (window_end + timedelta(days=1)).isoformat()

    closes: dict[str, pd.Series] = {}
    for ticker in timelines.keys():
        try:
            closes[ticker] = prices.get_historical_close(ticker, start_str, end_str)
        except Exception:
            continue

    if not closes:
        return []

    # One shared date index per ticker, forward-filled so chart gaps are not zeros.
    idx = pd.Index(sorted({d for series in closes.values() for d in series.index}))
    if idx.empty:
        return []

    aligned: dict[str, pd.Series] = {}
    for ticker, series in closes.items():
        s = series.copy()
        s = s.reindex(idx).ffill()
        aligned[ticker] = s

    points: list[dict] = []
    for d_str in idx:
        d_obj = datetime.strptime(d_str, "%Y-%m-%d").date()
        if d_obj < window_start or d_obj > window_end:
            continue
        total = 0.0
        for ticker, timeline in timelines.items():
            qty = _quantity_on(timeline, d_obj)
            if qty <= 0:
                continue
            series = aligned.get(ticker)
            if series is None:
                continue
            close = series.loc[d_str]
            if pd.isna(close):
                continue
            total += qty * float(close)
        points.append({"date": d_str, "portfolio_value": round(total, 2)})

    return points


def compute_benchmark(performance: list[dict]) -> list[dict]:
    """Return cumulative-return comparison between the portfolio and SPY."""
    if not performance:
        return []

    first_value = next((p["portfolio_value"] for p in performance if p["portfolio_value"] > 0), None)
    if first_value is None:
        return []

    start_str = performance[0]["date"]
    end_obj = datetime.strptime(performance[-1]["date"], "%Y-%m-%d").date()
    end_str = (end_obj + timedelta(days=1)).isoformat()

    try:
        spy_raw = prices.get_historical_close("SPY", start_str, end_str)
    except Exception:
        return []

    if spy_raw.empty:
        return []

    # Align SPY closes to the portfolio dates and forward-fill so the benchmark
    # doesn't arbitrarily drop points due to missing date keys.
    perf_dates = pd.Index([p["date"] for p in performance])
    spy = spy_raw.reindex(perf_dates).ffill()
    if spy.empty:
        return []

    first_spy = next((float(v) for v in spy if v and not pd.isna(v)), None)
    if not first_spy:
        return []

    result: list[dict] = []
    for p in performance:
        d = p["date"]
        if d not in spy.index:
            continue
        spy_close = spy.loc[d]
        if pd.isna(spy_close):
            continue
        portfolio_return = (p["portfolio_value"] / first_value - 1) * 100
        benchmark_return = (float(spy_close) / first_spy - 1) * 100
        result.append(
            {
                "date": d,
                "portfolio_return": round(portfolio_return, 2),
                "benchmark_return": round(benchmark_return, 2),
            }
        )
    return result
