"""Command-line interface: a thin layer between the user and the library."""
from __future__ import annotations

import argparse
import logging
import sys
from datetime import datetime, timezone

from currency_converter.converter import (
    InvalidAmountError,
    convert_many,
    format_money,
    parse_amount,
)
from currency_converter.rates_client import RatesError
from currency_converter.service import get_snapshot

ATTRIBUTION = "Rates by ExchangeRate-API (https://www.exchangerate-api.com)"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="convert",
        description="Convert an amount between currencies using live exchange rates.",
    )
    parser.add_argument("amount", help="amount to convert, e.g. 100000 or 49.90")
    parser.add_argument("source", metavar="FROM", help="source currency code, e.g. COP")
    parser.add_argument("targets", metavar="TO", nargs="+", help="one or more target codes")
    parser.add_argument("-v", "--verbose", action="store_true", help="show technical details")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.ERROR,
        format="%(levelname)s %(name)s: %(message)s",
    )

    source = args.source.strip().upper()
    try:
        amount = parse_amount(args.amount)
        snapshot, is_stale = get_snapshot(source)
        results = convert_many(amount, source, args.targets, snapshot)
    except (RatesError, InvalidAmountError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    updated = datetime.fromtimestamp(snapshot.last_update_unix, tz=timezone.utc)
    print(f"{format_money(amount, source)} {source} =")
    for code, value in results.items():
        print(f"  {format_money(value, code):>16} {code}")
    print(f"\nRates updated {updated:%Y-%m-%d %H:%M} UTC | {ATTRIBUTION}")
    if is_stale:
        print("WARNING: the rates service is unavailable; these are saved rates.")
    return 0


if __name__ == "__main__":
    sys.exit(main())