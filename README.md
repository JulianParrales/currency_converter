# Currency Converter
 
A small, tested Python library and command-line tool that converts amounts between currencies using live exchange rates. It was built as a reusable core: the same conversion logic can power a CLI today and a Telegram bot, a WhatsApp bot, or a web API later.
 
## What it does
 
- Converts an amount between any two supported currencies (160+), including COP, USD, EUR and JPY.
- Converts to several currencies in one command.
- Keeps working when the rates service is down by falling back to saved rates, and tells the user when it does.
- Uses `Decimal` for all money math, so there are no floating-point surprises.
## Install
 
Requires Python 3.10 or newer.
 
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate
pip install -e .
```
 
For development (adds `pytest`):
 
```bash
pip install -e ".[dev]"
```
 
## Usage
 
```bash
convert 100000 COP EUR
convert 100 USD COP EUR JPY
```
 
Example output (the numbers are illustrative; real rates change daily):
 
```
100,000.00 COP =
             27.59 EUR
 
Rates updated 2026-10-09 00:31 UTC | Rates by ExchangeRate-API (https://www.exchangerate-api.com)
```
 
If the rates service cannot be reached and saved rates are used, the tool adds a warning line. Errors are printed as one clear line, for example `Error: Unsupported currency code: XXX.`, and the exit code is 1.
 
Options: `-v` / `--verbose` shows technical logging.
 
## Use as a library
 
```python
from currency_converter.service import get_snapshot
from currency_converter.converter import convert, convert_many, format_money
 
snapshot, is_stale = get_snapshot("USD")           # live rates, or saved rates if the service is down
eur = convert("100000", "COP", "EUR", snapshot)    # Decimal, rounded for the target currency
print(format_money(eur, "EUR"))
 
both = convert_many("100", "USD", ["EUR", "COP"], snapshot)
```
 
`is_stale` is `True` when the live service failed and saved rates were used. Show the user the update time (`snapshot.last_update_unix`) in that case.
 
## How it works
 
```
user input -> cli.py -> service.py -> cache.py (saved rates, no network if still fresh)
                                   -> rates_client.py (live API call, with timeout)
                     -> converter.py (pure math, validation, rounding)
```
 
| File | Responsibility |
| --- | --- |
| `rates_client.py` | Fetches rates from the API; validates the response; raises clear errors |
| `cache.py` | Saves and loads rate snapshots as JSON files |
| `service.py` | Chooses between fresh cache, live data and stale cache |
| `converter.py` | Amount parsing, conversion through USD, rounding, formatting |
| `cli.py` | The `convert` command |
 
The conversion logic has no network, printing or input code, so it can be reused anywhere and tested offline.
 
## Error handling
 
| Situation | What happens |
| --- | --- |
| Amount is not a number, is negative, `NaN` or `Infinity`, or uses separators like `100,000` | `InvalidAmountError` |
| Currency code is not 3 letters or not supported | `InvalidCurrencyError` |
| Service unreachable, timeout, HTTP 429/5xx | Saved rates are used if they are less than 7 days old; otherwise `RatesUnavailableError` |
| Service replies with unexpected data | Treated like unavailable; `InvalidResponseError` if no usable saved rates |
 
## Settings
 
| Setting | Meaning | Default |
| --- | --- | --- |
| `CURRENCY_CONVERTER_CACHE_DIR` | Folder where saved rates are stored | `~/.cache/currency_converter` |
 
The maximum age of saved rates is `MAX_STALE_SECONDS` in `service.py` (7 days).
 
## Tests
 
```bash
pytest
```
 
Tests run offline and cover conversion, rounding, bad input, and the cache and fallback logic.
 
## Data source and attribution
 
Exchange rates are provided by [ExchangeRate-API](https://www.exchangerate-api.com) through its open access endpoint (`open.er-api.com`). Attribution is required by their terms, and this project shows it in the CLI output. Rates update once a day.
 
## Limitations
 
- Rates update once per day, so this is not suitable for trading or for accounting that needs exact settlement rates.
- Rounding uses common decimal places per currency (2 by default; 0 for JPY, KRW, CLP, VND; 3 for BHD, KWD). The list in `converter.py` is not exhaustive.
- Amounts must be plain numbers (`100000` or `100000.50`); locale formats are not parsed.
## Roadmap
 
- Spanish interface text.
- Telegram and WhatsApp adapters on top of the same core.
- Retry on temporary network errors.
## License
 
To be decided.
 