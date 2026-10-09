"""Local cache for rate snapshots: one JSON file per base currency."""
from __future__ import annotations

import json
import logging
import os
from decimal import Decimal, InvalidOperation
from pathlib import Path

from currency_converter.rates_client import RatesSnapshot

logger = logging.getLogger(__name__)


def default_cache_dir() -> Path:
    override = os.environ.get("CURRENCY_CONVERTER_CACHE_DIR")
    return Path(override) if override else Path.home() / ".cache" / "currency_converter"


def save_snapshot(snapshot: RatesSnapshot, cache_dir: Path | str | None = None) -> None:
    directory = Path(cache_dir) if cache_dir else default_cache_dir()
    data = {
        "base": snapshot.base,
        "rates": {code: str(value) for code, value in snapshot.rates.items()},
        "last_update_unix": snapshot.last_update_unix,
        "next_update_unix": snapshot.next_update_unix,
    }
    try:
        directory.mkdir(parents=True, exist_ok=True)
        target = directory / f"{snapshot.base}.json"
        temp = target.with_suffix(".tmp")
        temp.write_text(json.dumps(data), encoding="utf-8")
        temp.replace(target)  # atomic: never leaves a half-written file
    except OSError:
        logger.warning("Could not write the rates cache.", exc_info=True)


def load_snapshot(base: str, cache_dir: Path | str | None = None) -> RatesSnapshot | None:
    directory = Path(cache_dir) if cache_dir else default_cache_dir()
    path = directory / f"{base}.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return RatesSnapshot(
            base=data["base"],
            rates={code: Decimal(value) for code, value in data["rates"].items()},
            last_update_unix=int(data["last_update_unix"]),
            next_update_unix=int(data["next_update_unix"]),
        )
    except FileNotFoundError:
        return None
    except (OSError, ValueError, KeyError, TypeError, AttributeError, InvalidOperation):
        logger.warning("Ignoring unreadable cache file %s", path)
        return None