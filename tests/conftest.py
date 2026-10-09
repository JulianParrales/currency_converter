from decimal import Decimal

import pytest

from currency_converter.rates_client import RatesSnapshot


@pytest.fixture
def snapshot():
    return RatesSnapshot(
        base="USD",
        rates={
            "USD": Decimal("1"),
            "COP": Decimal("4000"),
            "EUR": Decimal("0.5"),
            "JPY": Decimal("150"),
        },
        last_update_unix=1_000,
        next_update_unix=2_000,
    )