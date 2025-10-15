"""Conversational agent that maps natural-language questions to BMA metrics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional


from student_registration.backends.ai_service import execute_metric
from student_registration.backends.models import Metric
from student_registration.backends.nl_resolver import nl_to_metric_payload, sanitize_payload
from student_registration.backends.similarity import MetricDocument, MetricSimilarityIndex


@dataclass(frozen=True)
class MetricSuggestion:
    """Lightweight suggestion returned by the similarity search."""

    metric_key: str
    label: str
    summary: str


class BMAMetricsAgent:
    """Resolve natural-language questions into metric queries and results."""

    class AgentError(RuntimeError):
        """Raised when the agent cannot serve the request."""

        def __init__(self, message: str, *, status_code: int = 400):
            super().__init__(message)
            self.status_code = status_code

    def __init__(
        self,
        user,
        *,
        metrics: Optional[Iterable[Metric]] = None,
        similarity_index: Optional[MetricSimilarityIndex] = None,
    ) -> None:
        self.user = user
        self.metrics: List[Metric] = list(metrics or Metric.objects.all())
        self._similarity_index = similarity_index
        if self._similarity_index is None and self.metrics:
            try:
                self._similarity_index = MetricSimilarityIndex(self.metrics)
            except Exception:
                self._similarity_index = None

    # ------------------------------------------------------------------
    def answer(
        self,
        question: str,
        *,
        top_k: int = 3,
        include_suggestions: bool = True,
    ) -> Dict[str, Any]:
        """Return a metric query, the execution result and optional suggestions."""

        cleaned_question = (question or "").strip()
        if not cleaned_question:
            raise self.AgentError("A natural-language question is required.")

        if not self.metrics:
            raise self.AgentError(
                "No metrics are configured for the BMA assistant.", status_code=503
            )

        suggestions = self._similar_metrics(cleaned_question, top_k=top_k)
        payload = self._build_payload(cleaned_question, suggestions)
        metric = self._resolve_metric(payload, suggestions)
        normalized = self._normalise_payload(payload, metric)
        result = self._execute_metric(normalized)

        response: Dict[str, Any] = {
            "query": normalized,
            "result": result,
            "selected_metric": {
                "key": metric.key,
                "label": metric.label,
                "description": metric.description,
                "sql_view": metric.sql_view,
            },
            "explanation": self._summarise(metric, normalized, result),
        }

        if include_suggestions and suggestions:
            response["similarity_suggestions"] = [
                {
                    "metric_key": suggestion.metric_key,
                    "label": suggestion.label,
                    "summary": suggestion.summary,
                }
                for suggestion in suggestions
            ]

        return response

    # ------------------------------------------------------------------
    def _build_payload(
        self, question: str, suggestions: List[MetricSuggestion]
    ) -> Dict[str, Any]:
        payload = sanitize_payload(nl_to_metric_payload(question))

        # If the heuristic resolver did not pick a known metric, try the similarity match.
        metric_keys = {metric.key for metric in self.metrics}
        metric_key = payload.get("metric_key")
        if metric_key not in metric_keys:
            for suggestion in suggestions:
                if suggestion.metric_key in metric_keys:
                    payload["metric_key"] = suggestion.metric_key
                    break

        # Ensure we at least default to the first available metric.
        if payload.get("metric_key") not in metric_keys:
            payload["metric_key"] = self.metrics[0].key

        return payload

    def _resolve_metric(
        self, payload: Dict[str, Any], suggestions: List[MetricSuggestion]
    ) -> Metric:
        key = payload.get("metric_key")
        metric = next((m for m in self.metrics if m.key == key), None)
        if metric:
            return metric

        for suggestion in suggestions:
            metric = next((m for m in self.metrics if m.key == suggestion.metric_key), None)
            if metric:
                payload["metric_key"] = metric.key
                return metric

        # As a very last resort, fall back to the first metric.
        metric = self.metrics[0]
        payload["metric_key"] = metric.key
        return metric

    def _normalise_payload(self, payload: Dict[str, Any], metric: Metric) -> Dict[str, Any]:
        normalized = dict(payload)
        time_range = normalized.get("time_range") or {}
        start = time_range.get("start")
        end = time_range.get("end")
        if not start or not end:
            normalized["time_range"] = self._default_time_range()
        else:
            normalized["time_range"] = {"start": start, "end": end}

        allowed_breakdowns = [
            b for b in (metric.allowed_breakdowns or []) if b and b != "none"
        ]
        breakdowns = [
            b for b in (normalized.get("breakdowns") or []) if b in allowed_breakdowns
        ][:3]
        if not breakdowns and allowed_breakdowns:
            breakdowns = allowed_breakdowns[:1]
        normalized["breakdowns"] = breakdowns

        breakdown_by = normalized.get("breakdown_by")
        if breakdown_by not in breakdowns:
            normalized["breakdown_by"] = breakdowns[0] if breakdowns else "none"
        else:
            normalized["breakdown_by"] = breakdown_by or "none"

        allowed_filters = set(metric.allowed_filters or [])
        normalized["filters"] = [
            f
            for f in (normalized.get("filters") or [])
            if f.get("field") in allowed_filters
        ]

        return normalized

    def _execute_metric(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        time_range = payload.get("time_range", {})
        try:
            return execute_metric(
                metric_key=payload["metric_key"],
                breakdown_by=payload.get("breakdown_by", "none"),
                time_start=time_range["start"],
                time_end=time_range["end"],
                filters=payload.get("filters", []),
                user_ctx=self._build_user_context(),
            )
        except BMAMetricsAgent.AgentError:
            raise
        except PermissionError as exc:
            raise self.AgentError(str(exc), status_code=403) from exc
        except KeyError as exc:
            raise self.AgentError("Metric query is missing a time range.") from exc
        except Exception as exc:
            raise self.AgentError("Failed to execute the metric query.", status_code=502) from exc

    def _build_user_context(self) -> Dict[str, Any]:
        user = getattr(self, "user", None)
        if not user:
            return {}

        partner_ids = []
        partner_attr = getattr(user, "partner_ids", None)
        if callable(partner_attr):
            try:
                partner_ids = list(partner_attr())
            except Exception:
                partner_ids = []
        elif partner_attr is not None:
            try:
                partner_ids = list(partner_attr)
            except TypeError:
                partner_ids = []

        roles: List[str] = []
        groups = getattr(user, "groups", None)
        if groups is not None:
            try:
                roles = list(groups.values_list("name", flat=True))
            except Exception:
                try:
                    roles = [getattr(group, "name", "") for group in groups.all()]
                except Exception:
                    roles = []

        return {
            "user_id": getattr(user, "id", None),
            "partner_ids": [pid for pid in partner_ids if pid],
            "roles": [role for role in roles if role],
        }

    def _similar_metrics(
        self, question: str, *, top_k: int
    ) -> List[MetricSuggestion]:
        index = self._similarity_index
        if not index:
            return []
        try:
            documents = index.search(question, top_k=top_k)
        except Exception:
            return []
        return [self._to_suggestion(doc) for doc in documents]

    @staticmethod
    def _to_suggestion(document: MetricDocument) -> MetricSuggestion:
        key = document.metadata.get("metric_key") or document.key
        label = document.metadata.get("label") or key
        return MetricSuggestion(metric_key=key, label=label, summary=document.summary)

    @staticmethod
    def _default_time_range() -> Dict[str, str]:
        end = date.today()
        start = end - timedelta(days=180)
        return {"start": start.isoformat(), "end": end.isoformat()}

    def _summarise(
        self,
        metric: Metric,
        query: Dict[str, Any],
        result: Dict[str, Any],
    ) -> str:
        label = metric.label or metric.key
        time_range = query.get("time_range", {})
        start = time_range.get("start")
        end = time_range.get("end")
        breakdown = query.get("breakdown_by")
        pieces = [f"Metric '{label}'"]
        if start and end:
            pieces.append(f"from {start} to {end}")
        if breakdown and breakdown != "none":
            pieces.append(f"broken down by {breakdown}")
        summary = " ".join(pieces) + "."

        total = result.get("total")
        if total is not None:
            unit = result.get("unit") or "value"
            summary += f" Reported total: {total} {unit}."
        elif "rows" in result:
            summary += f" Returned {len(result.get('rows', []))} rows."

        last_updated = result.get("last_modified") or result.get("generated_at")
        if last_updated:
            summary += f" Data last updated at {last_updated}."

        return summary

