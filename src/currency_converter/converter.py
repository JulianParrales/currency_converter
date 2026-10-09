"""Pure conversion logic: no network, no printing, no input()."""
from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

from currency_converter.rates_client import InvalidCurrencyError, RatesSnapshot

# Currencies that do not use 2 decimal places (partial list).
DECIMALS = {"JPY": 0, "KRW": 0, "CLP": 0, "VND": 0, "BHD": 3, "KWD": 3}
DEFAULT_DECIMALS = 2


class InvalidAmountError(ValueError):
    """The amount is not a valid, non-negative number."""


def parse_amount(amount: Decimal | int | float | str) -> Decimal:
    """Turn user input into a safe Decimal, or raise InvalidAmountError."""
    try:
        value = Decimal(str(amount).strip())
    except InvalidOperation as exc:
        raise InvalidAmountError(f"{amount!r} is not a valid number.") from exc
    if not value.is_finite():
        raise InvalidAmountError("Amount must be a finite number.")
    if value < 0:
        raise InvalidAmountError("Amount cannot be negative.")
    return value


def round_money(value: Decimal, currency: str) -> Decimal:
    """Round to the usual number of decimal places for a currency."""
    places = DECIMALS.get(currency, DEFAULT_DECIMALS)
    return value.quantize(Decimal(1).scaleb(-places), rounding=ROUND_HALF_UP)


def _get_rate(code: str, snapshot: RatesSnapshot) -> Decimal:
    try:
        return snapshot.rates[code]
    except KeyError as exc:
        raise InvalidCurrencyError(f"Currency {code!r} is not available.") from exc


def convert(
        amount: Decimal | int | float | str,
        from_currency: str,
        to_currency: str,
        snapshot: RatesSnapshot,
        *,
        round_result: bool = True,
) -> Decimal:
    """Convert an amount between two currencies using one rates snapshot."""
    value = parse_amount(amount)
    source = from_currency.strip().upper()
    target = to_currency.strip().upper()

    result = value * _get_rate(target, snapshot) / _get_rate(source, snapshot)
    return round_money(result, target) if round_result else result


def format_money(value: Decimal, currency: str) -> str:
    """Format like 1,234.50 using the right decimals for the currency."""
    places = DECIMALS.get(currency, DEFAULT_DECIMALS)
    return f"{value:,.{places}f}"


def convert_many(amount, from_currency, to_currencies, snapshot) -> dict[str, Decimal]:
    """Convert to several currencies. All-or-nothing: one bad code fails the call."""
    return {
        code.strip().upper(): convert(amount, from_currency, code, snapshot)
        for code in to_currencies
    }