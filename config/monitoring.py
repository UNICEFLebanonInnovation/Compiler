"""Utilities for configuring Azure Monitor via OpenTelemetry.

This module centralizes the logic that enables Azure Monitor telemetry for the
project.  It relies on the ``azure-monitor-opentelemetry`` distribution to
wire up OpenTelemetry exporters and instrumentation from
``opentelemetry-python-contrib``.

The configuration is intentionally idempotent so that importing this module
from different entry-points (Django, Celery, etc.) does not result in duplicate
instrumentation being registered.
"""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
from functools import lru_cache
from typing import Any, Dict

logger = logging.getLogger(__name__)

_CONFIGURED = False


def configure_azure_monitoring(*, service_name: str | None = None) -> bool:
    """Configure Azure Monitor OpenTelemetry instrumentation.

    Parameters
    ----------
    service_name:
        Optional explicit service name for the OpenTelemetry resource.  If not
        provided, ``AZURE_MONITOR_SERVICE_NAME`` or ``OTEL_SERVICE_NAME`` from
        the environment will be used, defaulting to ``"student-registration"``.

    Returns
    -------
    bool
        ``True`` when instrumentation was successfully configured.  ``False``
        indicates that configuration was skipped, either because a connection
        string was not supplied or instrumentation had already been applied.
    """

    global _CONFIGURED

    if _CONFIGURED:
        logger.debug("Azure Monitor OpenTelemetry already configured; skipping")
        return False

    connection_string = _connection_string()
    if not connection_string:
        logger.debug(
            "Azure Monitor connection string not provided; telemetry disabled"
        )
        return False

    otel_service_name = _resolve_service_name(service_name)
    os.environ.setdefault("OTEL_SERVICE_NAME", otel_service_name)

    azure_monitor_spec = importlib.util.find_spec("azure.monitor.opentelemetry")
    if azure_monitor_spec is None:
        logger.debug(
            "azure.monitor.opentelemetry package not available; skipping telemetry"
        )
        return False

    azure_monitor_module = importlib.import_module("azure.monitor.opentelemetry")
    configure_azure_monitor = getattr(azure_monitor_module, "configure_azure_monitor")

    configure_azure_monitor(**_configuration_options())

    _instrument_if_available(
        module_name="opentelemetry.instrumentation.django",
        instrumentor_attribute="DjangoInstrumentor",
    )
    _instrument_if_available(
        module_name="opentelemetry.instrumentation.celery",
        instrumentor_attribute="CeleryInstrumentor",
    )

    _CONFIGURED = True
    logger.info(
        "Azure Monitor OpenTelemetry configured for service '%s'", otel_service_name
    )
    return True


def _connection_string() -> str | None:
    connection_string = _value_from_env_or_settings(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "AZURE_MONITOR_CONNECTION_STRING",
    )
    if connection_string:
        if _contains_instrumentation_key(connection_string):
            return connection_string

        logger.warning(
            "Azure Monitor connection string missing InstrumentationKey; telemetry disabled"
        )
        return None

    instrumentation_key = _instrumentation_key()
    if not instrumentation_key:
        return None

    parts = [f"InstrumentationKey={instrumentation_key}"]

    ingestion_endpoint = _value_from_env_or_settings("AZURE_MONITOR_INGESTION_ENDPOINT")
    if ingestion_endpoint:
        parts.append(f"IngestionEndpoint={ingestion_endpoint}")

    live_endpoint = _value_from_env_or_settings("AZURE_MONITOR_LIVE_ENDPOINT")
    if live_endpoint:
        parts.append(f"LiveEndpoint={live_endpoint}")

    application_id = _value_from_env_or_settings("AZURE_MONITOR_APPLICATION_ID")
    if application_id:
        parts.append(f"ApplicationId={application_id}")

    return ";".join(parts)


def _instrumentation_key() -> str | None:
    return _value_from_env_or_settings(
        "AZURE_MONITOR_INSTRUMENTATION_KEY",
        "APPLICATIONINSIGHTS_INSTRUMENTATION_KEY",
        "APPINSIGHTS_INSTRUMENTATIONKEY",
    )


def _resolve_service_name(service_name: str | None) -> str:
    if service_name:
        return service_name
    return os.getenv(
        "AZURE_MONITOR_SERVICE_NAME",
        os.getenv("OTEL_SERVICE_NAME", "student-registration"),
    )


def _configuration_options() -> Dict[str, Any]:
    options: Dict[str, Any] = {}

    disable_tracing = _value_from_env_or_settings("AZURE_MONITOR_DISABLE_TRACING")
    if disable_tracing is not None:
        options["disable_tracing"] = _as_bool(disable_tracing)

    disable_metrics = _value_from_env_or_settings("AZURE_MONITOR_DISABLE_METRICS")
    if disable_metrics is not None:
        metrics_disabled = _as_bool(disable_metrics)
        options["disable_metrics"] = metrics_disabled

        if not metrics_disabled and _has_instrumentation_key():
            options["enable_live_metrics"] = True

    disable_logging = _value_from_env_or_settings("AZURE_MONITOR_DISABLE_LOGGING")
    if disable_logging is not None:
        options["disable_logging"] = _as_bool(disable_logging)

    sampling_ratio = _value_from_env_or_settings("AZURE_MONITOR_SAMPLING_RATIO")
    if sampling_ratio not in (None, ""):
        try:
            options["sampling_ratio"] = float(sampling_ratio)
        except (TypeError, ValueError):
            logger.warning(
                "Invalid AZURE_MONITOR_SAMPLING_RATIO '%s'; expected float", sampling_ratio
            )

    return options


def _has_instrumentation_key() -> bool:
    if _instrumentation_key():
        return True

    connection_string = _value_from_env_or_settings(
        "APPLICATIONINSIGHTS_CONNECTION_STRING",
        "AZURE_MONITOR_CONNECTION_STRING",
    )

    if connection_string:
        return _contains_instrumentation_key(connection_string)

    return False


def _value_from_env_or_settings(*names: str) -> str | None:
    for name in names:
        value = os.getenv(name)
        if value:
            return value

        settings_value = _settings_value(name)
        if settings_value not in (None, ""):
            return str(settings_value)
    return None


@lru_cache(maxsize=None)
def _settings_value(name: str) -> Any | None:
    module_names = []
    settings_module = os.getenv("DJANGO_SETTINGS_MODULE")
    if settings_module:
        module_names.append(settings_module)

    # Fall back to the production settings module when DJANGO_SETTINGS_MODULE is
    # not yet populated (e.g. early in the WSGI bootstrap).
    module_names.append("config.settings.production")

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue

        if hasattr(module, name):
            value = getattr(module, name)
            if value not in (None, ""):
                return value

    try:
        from django.conf import settings  # type: ignore
    except Exception:
        return None

    if getattr(settings, "configured", False) and hasattr(settings, name):
        value = getattr(settings, name)
        if value not in (None, ""):
            return value

    return None


def _as_bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in {"1", "true", "yes", "on"}


def _contains_instrumentation_key(connection_string: str) -> bool:
    for part in connection_string.split(";"):
        key, _, value = part.partition("=")
        if key.strip().lower() == "instrumentationkey":
            return bool(value.strip())
    return False


def _instrument_if_available(module_name: str, instrumentor_attribute: str) -> None:
    module_spec = importlib.util.find_spec(module_name)
    if module_spec is None:
        logger.debug("Instrumentation module '%s' not available", module_name)
        return

    module = importlib.import_module(module_name)
    instrumentor = getattr(module, instrumentor_attribute)()

    if getattr(instrumentor, "is_instrumented", None):
        if instrumentor.is_instrumented():  # type: ignore[call-arg]
            logger.debug("%s already instrumented", instrumentor_attribute)
            return

    instrumentor.instrument()

