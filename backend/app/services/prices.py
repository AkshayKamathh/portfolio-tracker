"""Live and historical quotes through yfinance, with a short TTL cache."""

import time
from typing import Any

import pandas as pd
import yfinance as yf

from app import config

_CACHE_TTL_SECONDS = config.YF_CACHE_TTL or 60
_CACHE: dict[tuple, tuple[float, Any]] = {}


def _cache_get(key: tuple):
    entry = _CACHE.get(key)
    if entry is None:
        return None
    timestamp, value = entry
    if time.time() - timestamp > _CACHE_TTL_SECONDS:
        _CACHE.pop(key, None)
        return None
    return value


def _cache_set(key: tuple, value: Any) -> None:
    _CACHE[key] = (time.time(), value)


def clear_cache() -> None:
    _CACHE.clear()


def get_current_price(ticker: str) -> float:
    """Latest price: fast_info when present, else last close from a short history."""
    symbol = (ticker or "").strip().upper()
    if not symbol:
        raise ValueError("Ticker must not be empty")

    cached = _cache_get(("current", symbol))
    if cached is not None:
        return cached

    yf_ticker = yf.Ticker(symbol)

    try:
        fast_info = getattr(yf_ticker, "fast_info", None)
        if fast_info is not None:
            last_price = None
            try:
                last_price = fast_info["last_price"]
            except (KeyError, TypeError):
                last_price = getattr(fast_info, "last_price", None)
            if last_price is not None and not pd.isna(last_price):
                price = float(last_price)
                _cache_set(("current", symbol), price)
                return price
    except Exception:
        pass

    history = yf_ticker.history(period="5d")
    if history is None or history.empty or "Close" not in history:
        raise ValueError(f"No price data for {symbol}")
    price = float(history["Close"].dropna().iloc[-1])
    _cache_set(("current", symbol), price)
    return price


def get_historical_close(ticker: str, start_date: str, end_date: str) -> pd.Series:
    """Daily closes indexed by `YYYY-MM-DD` strings."""
    symbol = (ticker or "").strip().upper()
    if not symbol:
        raise ValueError("Ticker must not be empty")

    key = ("history", symbol, start_date, end_date)
    cached = _cache_get(key)
    if cached is not None:
        return cached

    data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=False,
    )
    if data is None or data.empty or "Close" not in data:
        raise ValueError(f"No price data for {symbol}")

    close = data["Close"]
    if isinstance(close, pd.DataFrame):
        close = close.iloc[:, 0]
    close = close.dropna()
    close.index = pd.to_datetime(close.index).strftime("%Y-%m-%d")
    close.name = symbol
    _cache_set(key, close)
    return close
