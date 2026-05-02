"""Shared rules for transaction dates (catch typos, keep charts sane)."""

from datetime import date

MIN_TRANSACTION_DATE = date(1970, 1, 1)
MAX_TRANSACTION_DATE = date(2100, 12, 31)


def validate_transaction_date(value: date) -> date:
    if value < MIN_TRANSACTION_DATE or value > MAX_TRANSACTION_DATE:
        raise ValueError(
            f"date must be between {MIN_TRANSACTION_DATE.isoformat()} "
            f"and {MAX_TRANSACTION_DATE.isoformat()}"
        )
    return value
