# Progress
 
Last updated: 2026-10-09
Mode: ship mode (fast, working, reusable products for local businesses). Learn mode on request.
 
## Goal
 
Ship functional, visually intuitive, reusable products for small local businesses, earn revenue, then sell the product or hire freelancers to extend it. If neither happens, each product still works as a local solution.
 
## Done
 
### Project 1: Currency converter (library + CLI) - complete
 
- Project skeleton with `src/` layout, `pyproject.toml`, `.gitignore`, `.env.example`
- `rates_client.py`: live rates from open.er-api.com, timeouts, 4 error types, Decimal parsing
- `converter.py`: validation, conversion through USD, half-up rounding, `convert_many`
- `cache.py` + `service.py`: saved rates, fresh-cache shortcut, stale fallback (max 7 days)
- `cli.py`: `convert 100000 COP EUR`, clear errors, attribution, stale warning
- Tests with `pytest`: all passing (converter, cache, service)
- README written
## Concepts used (practical level)
 
- Virtual environments, `pip install -e`, `src/` layout
- Secrets in `.env`, never committed; `.env.example` is committed
- Network calls need timeouts; separate error types for separate reactions
- `Decimal` for money; round once at the end; half-up rounding
- Core library with no I/O + thin adapters (CLI now, bots later)
- Cache with freshness rule and maximum age
- Offline tests using fake data and `monkeypatch`
## Decisions made
 
- API: open.er-api.com (no key, COP supported, once-daily, attribution required). Frankfurter was considered but not verified.
- `convert_many` is all-or-nothing (a partial answer looks like a complete one).
- Max age of saved rates: 7 days.
- Negative amounts are rejected; zero is allowed.
## Minimum bar checklist (can I operate and sell this?)
 
- [ ] Explain what it does and doesn't do in plain words
- [ ] Where do I change the provider if the API shuts down? (answer: `rates_client.py`; `service.py` only if the function name changes)
- [ ] How do I know if saved rates were used? (the CLI warning, `is_stale`, and `-v` logs)
- [ ] Which command checks nothing broke? (`pytest`)
- [ ] Where do settings and secrets live? (`.env`, environment variables)
## Open items
 
- [ ] Commit and push to GitHub (`01-currency-converter`); make sure `.idea/` is in `.gitignore`
- [ ] Optional challenge: retry up to 3 times on temporary errors (only errors worth retrying)
- [ ] Optional check: open `https://open.er-api.com/v6/latest/XXX` and confirm the `unsupported-code` assumption
- [ ] Decide on a license
## Business side
 
- [ ] Talk to 3 local businesses (barbershop, restaurant, clinic/salon): how they take bookings or orders, what goes wrong, would they pilot for 2 weeks?
- [ ] Choose one niche to focus on
- [ ] Draft a one-page offer and a 2-minute demo script
- Pricing idea: setup fee + monthly support/hosting (to be set after interviews)
## Next
 
1. Create the Telegram bot token with @BotFather (store it in `.env`, never in chat or code)
2. Project 11: Telegram command bot, reusing the converter library
3. Same bot brain on WhatsApp Cloud API (projects 31-34): menu, booking, reminders
4. Projects 12, 15, 16 (FAQ, booking, conversation flow), then 21, 23, 26, 27 (API, webhooks, scheduler, deploy)
## Log
 
- 2026-10-09: Project 1 finished in ship mode; README and PROGRESS created.
 