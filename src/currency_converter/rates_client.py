"""Client for the ExchangeRate-API open access endpoint.

Data provided by https://www.exchangerate-api.com (attribution required)
"""
from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation

import requests

logger = logging.getLogger(__name__)

BASE_URL = "https://open.er-api.com/v6/latest"
DEFAULT_TIMEOUT = 10 # seconds


class RatesError(Exception):
    """Base class for every error this module raises."""


class RatesUnavailableError(RatesError):
    """Service unreachable or failing. Retrying or using cached data may help."""


class InvalidCurrencyError(RatesError):
    """The currency code is not valid. Retrying will not help."""


class InvalidResponseError(RatesError):
    """The service answered, but the data was not what we expected."""


@dataclass(frozen=True)
class RatesSnapshot:
    base: str
    rates: dict[str, Decimal]
    last_update_unix: int
    next_update_unix: int


def normalize_code(code: str) -> str:
    """Return an upper-case 3-letter currency code or raise InvalidCurrencyError."""
    code = code.strip().upper()
    if not (len(code) == 3 and code.isascii() and code.isalpha()):
        raise InvalidCurrencyError(f"{code!r} is not a valid 3-letter currency code.")
    return code

def fetch_rates(base: str, timeout: float = DEFAULT_TIMEOUT) -> RatesSnapshot:
    """Fetch all exchange rates for one base currency."""
    base = normalize_code(base)

    try:
        response = requests.get(f"{BASE_URL}/{base}", timeout=timeout)
    except requests.Timeout as exc:
        raise RatesUnavailableError("The rates service took too long to respond.") from exc
    except requests.RequestException as exc:
        raise RatesUnavailableError("Could not reach the rates service.") from exc

    if response.status_code == 429 or response.status_code >= 500:
        raise RatesUnavailableError(f"Rates service returned HTTP {response.status_code}.")

    try:
        payload = json.loads(response.text, parse_float=Decimal)
    except ValueError as exc:
        raise InvalidResponseError("The rates service did not return valid JSON.") from exc

    if not isinstance(payload, dict):
        raise InvalidResponseError("Unexpected response format.")

    if payload.get("result") != "success":
        error_type = payload.get("error-type", "unknown")
        if error_type == "unsupported_code":
            raise InvalidCurrencyError(f"Unsupported currency code: {base}.")
        raise RatesUnavailableError(f"Rates service reported an error: {error_type}.")

    try:
        rates: dict[str, Decimal] = {}
        for code, raw in payload["rates"].items():
            value = Decimal(str(raw))
            if not value.is_finite() or value <= 0:
                raise ValueError(f"bad rate for {code}")
            rates[code] = value
        snapshot = RatesSnapshot(
            base=payload["base_code"],
            rates=rates,
            last_update_unix=int(payload["time_last_update_unix"]),
            next_update_unix=int(payload["time_next_update_unix"])
        )
    except (KeyError, TypeError, ValueError, AttributeError, InvalidOperation) as exc:
        raise InvalidResponseError("The rates data had an unexpected format.") from exc

    logger.info("Fetched %d rates for %s", len(snapshot.rates), snapshot.base)
    return snapshot