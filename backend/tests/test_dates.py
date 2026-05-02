"""Unit tests for transaction date bounds."""

from datetime import date

import pytest

from app.utils.dates import (
    MAX_TRANSACTION_DATE,
    MIN_TRANSACTION_DATE,
    validate_transaction_date,
)


def test_validate_accepts_edges():
    assert validate_transaction_date(MIN_TRANSACTION_DATE) == MIN_TRANSACTION_DATE
    assert validate_transaction_date(MAX_TRANSACTION_DATE) == MAX_TRANSACTION_DATE


def test_validate_rejects_before_1970():
    with pytest.raises(ValueError, match="between"):
        validate_transaction_date(date(1969, 12, 31))


def test_validate_rejects_after_2100():
    with pytest.raises(ValueError, match="between"):
        validate_transaction_date(date(2101, 1, 1))
