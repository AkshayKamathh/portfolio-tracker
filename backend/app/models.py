"""Pydantic models for request/response validation."""

from datetime import date
from typing import Literal, Optional

from pydantic import BaseModel, Field, field_validator


class TransactionCreate(BaseModel):
    ticker: str
    transaction_type: Literal["buy", "sell"]
    quantity: float = Field(..., gt=0)
    price: float = Field(..., gt=0)
    date: date

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str) -> str:
        cleaned = (value or "").strip().upper()
        if not cleaned:
            raise ValueError("ticker must not be empty")
        return cleaned


class TransactionUpdate(BaseModel):
    ticker: str | None = None
    transaction_type: Literal["buy", "sell"] | None = None
    quantity: float | None = None
    price: float | None = None
    date: Optional[date] = None

    @field_validator("ticker")
    @classmethod
    def normalize_ticker(cls, value: str | None) -> str | None:
        if value is None:
            return None
        cleaned = (value or "").strip().upper()
        if not cleaned:
            raise ValueError("ticker must not be empty")
        return cleaned

    @field_validator("quantity")
    @classmethod
    def quantity_positive_when_set(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("quantity must be greater than zero")
        return value

    @field_validator("price")
    @classmethod
    def price_positive_when_set(cls, value: float | None) -> float | None:
        if value is None:
            return None
        if value <= 0:
            raise ValueError("price must be greater than zero")
        return value


class TransactionResponse(BaseModel):
    id: str
    ticker: str
    transaction_type: str
    quantity: float
    price: float
    date: str
    created_at: str


class PortfolioAsset(BaseModel):
    ticker: str
    quantity: float
    avg_buy_price: float
    cost_basis: float
    current_price: float
    market_value: float
    gain_loss: float
    return_percent: float


class PortfolioSummary(BaseModel):
    total_value: float
    total_cost_basis: float
    total_gain_loss: float
    total_return_percent: float
    assets: list[PortfolioAsset]
    warnings: list[str] = []


class PerformancePoint(BaseModel):
    date: str
    portfolio_value: float


class BenchmarkPoint(BaseModel):
    date: str
    portfolio_return: float
    benchmark_return: float
