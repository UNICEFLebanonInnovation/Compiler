"""Tests for the Azure Monitor configuration helpers."""

from __future__ import annotations

import importlib

import pytest


@pytest.fixture(autouse=True)
def _clear_monitoring_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for name in (
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "AZURE_MONITOR_CONNECTION_STRING",
        "AZURE_MONITOR_INSTRUMENTATION_KEY",
        "APPLICATIONINSIGHTS_INSTRUMENTATION_KEY",
        "APPINSIGHTS_INSTRUMENTATIONKEY",
    ):
        monkeypatch.delenv(name, raising=False)


def _reload_monitoring():
    from config import monitoring

    importlib.reload(monitoring)
    monitoring._settings_value.cache_clear()  # type: ignore[attr-defined]
    return monitoring


def test_connection_string_with_instrumentation_key(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "InstrumentationKey=abc123;IngestionEndpoint=https://example",
    )

    monitoring = _reload_monitoring()

    assert (
        monitoring._connection_string()  # type: ignore[attr-defined]
        == "InstrumentationKey=abc123;IngestionEndpoint=https://example"
    )


def test_connection_string_without_instrumentation_key_is_ignored(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    monkeypatch.setenv(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "IngestionEndpoint=https://example",
    )

    monitoring = _reload_monitoring()

    with caplog.at_level("WARNING"):
        assert monitoring._connection_string() is None  # type: ignore[attr-defined]

    assert "connection string missing InstrumentationKey" in caplog.text
