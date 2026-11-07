"""
unit tests for invalid inputs to the model validation functions

run with: python -m pytest tests/test_models.py -v
"""

import pytest

from app.models import (
    ValidationError,
    validate_amount,
    validate_category,
    validate_date,
    validate_description,
    validate_title,
)

# parametrize runs each test once for every input value


# titles must be strings with 1–200 characters after stripping whitespace
@pytest.mark.parametrize("raw", [None, 123, "", "   ", "x" * 201])
def test_invalid_title(raw):
    with pytest.raises(ValidationError):
        validate_title(raw)


# amounts must be decimal strings: finite, positive, at most two decimal places
@pytest.mark.parametrize(
    "raw", ["abc", "0", "-1.00", "12.501", 12.50, None, "NaN", "Infinity"]
)
def test_invalid_amount(raw):
    with pytest.raises(ValidationError):
        validate_amount(raw)


# dates must represent real calendar dates in the exact YYYY-MM-DD format
@pytest.mark.parametrize(
    "raw", [None, 123, "", "2026-02-30", "2026-13-01", "06.11.2026", "20261106"]
)
def test_invalid_date(raw):
    with pytest.raises(ValidationError):
        validate_date(raw)


# categories must match an allowed, case-sensitive name after stripping whitespace
@pytest.mark.parametrize("raw", [None, 123, "", "   ", "Unknown", "food", "School"])
def test_invalid_category(raw):
    with pytest.raises(ValidationError):
        validate_category(raw)


# descriptions accept strings (including empty strings) or None; other types fail
@pytest.mark.parametrize("raw", [123, True, [], {}])
def test_invalid_description(raw):
    with pytest.raises(ValidationError):
        validate_description(raw)
