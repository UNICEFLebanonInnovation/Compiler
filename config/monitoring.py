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
    return (
        os.getenv("APPLICATIONINSIGHTS_CONNECTION_STRING")
        or os.getenv("AZURE_MONITOR_CONNECTION_STRING")
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

    disable_tracing = os.getenv("AZURE_MONITOR_DISABLE_TRACING")
    if disable_tracing is not None:
        options["disable_tracing"] = disable_tracing.lower() in {"1", "true", "yes"}

    disable_metrics = os.getenv("AZURE_MONITOR_DISABLE_METRICS")
    if disable_metrics is not None:
        options["disable_metrics"] = disable_metrics.lower() in {"1", "true", "yes"}

    disable_logging = os.getenv("AZURE_MONITOR_DISABLE_LOGGING")
    if disable_logging is not None:
        options["disable_logging"] = disable_logging.lower() in {"1", "true", "yes"}

    sampling_ratio = os.getenv("AZURE_MONITOR_SAMPLING_RATIO")
    if sampling_ratio:
        try:
            options["sampling_ratio"] = float(sampling_ratio)
        except ValueError:
            logger.warning(
                "Invalid AZURE_MONITOR_SAMPLING_RATIO '%s'; expected float", sampling_ratio
            )

    return options


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

