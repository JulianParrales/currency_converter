import pytest

from currency_converter import cache, service
from currency_converter.rates_client import RatesUnavailableError


def test_fresh_cache_skips_network(tmp_path, snapshot, monkeypatch):
    cache.save_snapshot(snapshot, tmp_path)
    monkeypatch.setattr(service, "fetch_rates", lambda base: pytest.fail("no network expected"))
    result, stale = service.get_snapshot("USD", cache_dir=tmp_path, now=1_500)
    assert result == snapshot and stale is False


def test_uses_old_cache_when_service_is_down(tmp_path, snapshot, monkeypatch):
    cache.save_snapshot(snapshot, tmp_path)

    def down(base):
        raise RatesUnavailableError("down")

    monkeypatch.setattr(service, "fetch_rates", down)
    result, stale = service.get_snapshot("USD", cache_dir=tmp_path, now=3_000)
    assert result == snapshot and stale is True


def test_refuses_cache_that_is_too_old(tmp_path, snapshot, monkeypatch):
    cache.save_snapshot(snapshot, tmp_path)

    def down(base):
        raise RatesUnavailableError("down")

    monkeypatch.setattr(service, "fetch_rates", down)
    with pytest.raises(RatesUnavailableError):
        service.get_snapshot("USD", cache_dir=tmp_path, now=100_000, max_stale_seconds=100)