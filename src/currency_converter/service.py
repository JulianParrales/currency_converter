"""Decides between cached and live rates."""
from __future__ import annotations

import logging
import time
from pathlib import Path

from currency_converter import cache
from currency_converter.rates_client import (
    InvalidResponseError,
    RatesSnapshot,
    RatesUnavailableError,
    fetch_rates,
    normalize_code,
)

logger = logging.getLogger(__name__)

MAX_STALE_SECONDS = 7 * 24 * 3600  # refuse cached rates older than 7 days


def get_snapshot(
    base: str,
    *,
    cache_dir: Path | str | None = None,
    max_stale_seconds: int = MAX_STALE_SECONDS,
    now: float | None = None,
) -> tuple[RatesSnapshot, bool]:
    """Return (snapshot, is_stale). is_stale=True means the live service failed."""
    base = normalize_code(base)
    now = time.time() if now is None else now

    cached = cache.load_snapshot(base, cache_dir)
    if cached and now < cached.next_update_unix:
        return cached, False  # still fresh: no network call at all

    try:
        fresh = fetch_rates(base)
    except (RatesUnavailableError, InvalidResponseError):
        if cached and now - cached.last_update_unix <= max_stale_seconds:
            logger.warning("Rates service failed; using cached rates for %s.", base)
            return cached, True
        raise

    cache.save_snapshot(fresh, cache_dir)
    return fresh, False