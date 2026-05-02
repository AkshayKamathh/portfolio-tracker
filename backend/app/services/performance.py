"""Portfolio history and SPY benchmark from stored transactions."""

from datetime import date, datetime, timedelta
from typing import Iterable

import pandas as pd

from app.services import prices
from app.services.holdings import _to_date, _sort_key, calculate_holdings


def _earliest_date(transactions: list[dict]) -> date | None:
    if not transactions:
        return None
    return min(_to_date(tx.get("date")) for tx in transactions)


def _latest_date(transactions: list[dict]) -> date | None:
    if not transactions:
        return None
    return max(_to_date(tx.get("date")) for tx in transactions)


def _quantity_timeline(transactions: list[dict]) -> dict[str, list[tuple[date, float]]]:
    """For each ticker: (date, quantity on hand) after each tx, in time order."""
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


def _live_portfolio_market_value(transactions: list[dict]) -> float:
    """Same notion of total value as /portfolio (live quote, avg buy fallback)."""
    total = 0.0
    for h in calculate_holdings(transactions):
        try:
            px = prices.get_current_price(h["ticker"])
        except Exception:
            px = h["avg_buy_price"]
        total += h["quantity"] * float(px)
    return round(total, 2)


def _performance_fallback_line(
    tx_list: list[dict],
    window_start: date,
    window_end: date,
) -> list[dict]:
    """Two points at live mark-to-market when daily history is missing."""
    timelines = _quantity_timeline(tx_list)
    if not timelines:
        return []
    mv = _live_portfolio_market_value(tx_list)
    if mv <= 0:
        return []
    d0 = window_start
    d1 = window_end if window_end > window_start else window_start + timedelta(days=1)
    return [
        {"date": d0.isoformat(), "portfolio_value": mv},
        {"date": d1.isoformat(), "portfolio_value": mv},
    ]


def _benchmark_without_spy_series(performance: list[dict], first_value: float) -> list[dict]:
    """Portfolio % vs first day; SPY leg set to 0% when SPY history is missing."""
    return [
        {
            "date": p["date"],
            "portfolio_return": round((p["portfolio_value"] / first_value - 1) * 100, 2),
            "benchmark_return": 0.0,
        }
        for p in performance
    ]


def _quantity_on(timeline: list[tuple[date, float]], target: date) -> float:
    """Position size on `target` from a single-ticker timeline."""
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
    """Daily `{date, portfolio_value}` inside the optional date window."""
    tx_list = list(transactions)
    if not tx_list:
        return []

    earliest = _earliest_date(tx_list)
    latest = _latest_date(tx_list)
    if earliest is None or latest is None:
        return []
    today = date.today()
    # Through max(today, last trade) so future-dated rows still have a valid window.
    ledger_end = max(today, latest)
    window_start = max(earliest, from_date) if from_date else earliest
    if to_date is not None:
        window_end = min(ledger_end, to_date)
    else:
        window_end = ledger_end
    if window_end < window_start:
        return []

    timelines = _quantity_timeline(tx_list)
    if not timelines:
        return []

    # Extra lookback so Yahoo usually returns at least a few bars for thin windows.
    fetch_pad = timedelta(days=120)
    fetch_start = window_start - fetch_pad
    if fetch_start < date(1970, 1, 1):
        fetch_start = date(1970, 1, 1)
    start_str = fetch_start.isoformat()
    end_str = (window_end + timedelta(days=1)).isoformat()  # yfinance end is exclusive

    closes: dict[str, pd.Series] = {}
    for ticker in timelines.keys():
        try:
            closes[ticker] = prices.get_historical_close(ticker, start_str, end_str)
        except Exception:
            continue

    if not closes:
        return _performance_fallback_line(tx_list, window_start, window_end)

    # Shared calendar across tickers; forward-fill so missing days are not zeroed out.
    idx = pd.Index(sorted({d for series in closes.values() for d in series.index}))
    if idx.empty:
        return _performance_fallback_line(tx_list, window_start, window_end)

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

    if not points:
        return _performance_fallback_line(tx_list, window_start, window_end)

    return points


def compute_benchmark(performance: list[dict]) -> list[dict]:
    """Cumulative % return vs SPY on the same dates as the performance series."""
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
        return _benchmark_without_spy_series(performance, first_value)

    if spy_raw.empty:
        return _benchmark_without_spy_series(performance, first_value)

    # Reindex SPY to portfolio dates and forward-fill missing bars.
    perf_dates = pd.Index([p["date"] for p in performance])
    spy = spy_raw.reindex(perf_dates).ffill()
    if spy.empty:
        return _benchmark_without_spy_series(performance, first_value)

    first_spy = next((float(v) for v in spy if v and not pd.isna(v)), None)
    if not first_spy:
        return _benchmark_without_spy_series(performance, first_value)

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
