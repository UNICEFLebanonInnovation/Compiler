from __future__ import annotations

from typing import Iterable, Sequence

from django.db.models import QuerySet

from .models import Metric


def _collect_unique(values: Iterable[Iterable[str]]) -> list[str]:
    seen = []
    for collection in values:
        for item in collection:
            if item and item not in seen:
                seen.append(item)
    return seen


def build_get_metric_tool(metrics: Sequence[Metric] | QuerySet | None = None) -> dict:
    """Build a JSON schema tool definition based on Metric metadata."""

    if metrics is None:
        metrics = Metric.objects.all()

    metric_keys = [m.key for m in metrics]
    breakdown_fields = _collect_unique(
        (m.allowed_breakdowns for m in metrics if getattr(m, "allowed_breakdowns", None))
    )
    filter_fields = _collect_unique(
        (m.allowed_filters for m in metrics if getattr(m, "allowed_filters", None))
    )

    breakdown_enum = [b for b in breakdown_fields if b and b != "none"]

    return {
        "type": "function",
        "function": {
            "name": "get_metric",
            "description": "Retrieve a metric with optional filters/breakdowns and time range.",
            "parameters": {
                "type": "object",
                "properties": {
                    "metric_key": {
                        "type": "string",
                        "enum": metric_keys,
                    },
                    "time_range": {
                        "type": "object",
                        "properties": {
                            "start": {"type": "string", "format": "date"},
                            "end": {"type": "string", "format": "date"},
                        },
                        "required": ["start", "end"],
                    },
                    "breakdown_by": {
                        "type": "string",
                        "enum": ["none", *breakdown_enum] if breakdown_enum else ["none"],
                    },
                    "breakdowns": {
                        "type": "array",
                        "items": {
                            "type": "string",
                            "enum": breakdown_enum,
                        },
                    },
                    "filters": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "field": {
                                    "type": "string",
                                    "enum": filter_fields,
                                },
                                "op": {
                                    "type": "string",
                                    "enum": ["=", "in", "between"],
                                },
                                "value": {},
                            },
                            "required": ["field", "op", "value"],
                        },
                    },
                },
                "required": ["metric_key", "time_range"],
            },
        },
    }
