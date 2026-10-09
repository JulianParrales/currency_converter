from decimal import Decimal

import pytest

from currency_converter.converter import InvalidAmountError, convert, convert_many
from currency_converter.rates_client import InvalidCurrencyError


def test_converts_through_usd(snapshot):
    assert convert("100000", "COP", "EUR", snapshot) == Decimal("12.50")


def test_rounds_half_up(snapshot):
    assert convert("2.665", "USD", "USD", snapshot) == Decimal("2.67")


def test_zero_decimal_currency(snapshot):
    assert convert("1", "USD", "JPY", snapshot) == Decimal("150")


@pytest.mark.parametrize("bad", ["abc", "-5", "NaN", "Infinity", "100,000", ""])
def test_rejects_bad_amounts(snapshot, bad):
    with pytest.raises(InvalidAmountError):
        convert(bad, "USD", "EUR", snapshot)


def test_unknown_currency(snapshot):
    with pytest.raises(InvalidCurrencyError):
        convert("1", "USD", "XXX", snapshot)


def test_convert_many_is_all_or_nothing(snapshot):
    with pytest.raises(InvalidCurrencyError):
        convert_many("1", "USD", ["EUR", "XXX"], snapshot)