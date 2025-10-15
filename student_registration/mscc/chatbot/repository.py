"""Data aggregation helpers for the BMA chatbot backed by materialised metrics."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Any, Dict, Iterable, List, Optional

from django.utils import timezone

from student_registration.backends.ai_service import execute_metric


class BMAInsightsRepository:
    """Aggregate MSCC/BMA data for natural-language insights using metrics."""

    registration_metric_key = "mscc_registrations_total"
    default_months = 6

    def __init__(self, user, *, time_range: Optional[Dict[str, str]] = None):
        self.user = user
        self._time_range = time_range or self._default_time_range(self.default_months)
        self._user_context = self._build_user_context(user)

    # Public API ----------------------------------------------------------------
    def build_snapshot(self) -> Dict[str, Any]:
        """Build a JSON-serialisable snapshot of the BMA dataset."""
        snapshot: Dict[str, Any] = {
            "generated_at": timezone.now().isoformat(),
            "time_range": dict(self._time_range),
            "scope": self._describe_scope(),
            "source": "metrics",
            "registrations": self._registration_snapshot(),
            "schools": self._empty_collection_snapshot("schools"),
            "centers": self._empty_collection_snapshot("centers"),
        }
        return snapshot

    # Registration helpers ------------------------------------------------------
    def _registration_snapshot(self) -> Dict[str, Any]:
        total = self._metric_total()
        snapshot = {
            "total": total,
            "time_range": dict(self._time_range),
            "records": [],  # record level data not available from materialised views
            "by_round": self._metric_breakdown("round_id", label_key="round"),
            "by_gender": self._metric_breakdown("child_gender_norm", label_key="gender"),
            "by_nationality": self._metric_breakdown(
                "child_nationality_name", label_key="nationality", limit=10
            ),
            "by_partner": self._metric_breakdown("partner_id", label_key="partner", limit=10),
            "by_package_type": self._metric_breakdown("cycle", label_key="package_type"),
            "by_governorate": self._metric_breakdown(
                "governorate", label_key="governorate", limit=10
            ),
            "monthly_trend": self._monthly_trend(months=12),
        }
        return snapshot

    def _metric_total(self) -> int:
        result = self._execute_metric("none")
        total = result.get("total")
        return int(total) if isinstance(total, (int, float)) else int(total or 0)

    def _metric_breakdown(
        self,
        breakdown: str,
        *,
        label_key: str,
        limit: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        result = self._execute_metric(breakdown)
        rows: Iterable[Dict[str, Any]] = result.get("rows", []) or []
        items: List[Dict[str, Any]] = []
        for row in rows:
            label = self._normalise_value(row.get("label"))
            value = row.get("value")
            try:
                count = int(value)
            except (TypeError, ValueError):
                count = 0
            items.append({label_key: label, "count": count})

        if limit is not None:
            items = items[:limit]
        return items

    def _monthly_trend(self, *, months: int = 12) -> List[Dict[str, Any]]:
        result = self._execute_metric("month")
        rows: Iterable[Dict[str, Any]] = result.get("rows", []) or []
        points: List[Dict[str, Any]] = []
        for row in rows:
            month = self._format_month(row.get("label"))
            if not month:
                continue
            value = row.get("value")
            try:
                count = int(value)
            except (TypeError, ValueError):
                count = 0
            points.append({"month": month, "registrations": count})

        if months:
            points = points[-months:]
        return points

    # Collection helpers --------------------------------------------------------
    @staticmethod
    def _empty_collection_snapshot(name: str) -> Dict[str, Any]:
        base = {"total": 0}
        if name == "schools":
            base.update({"by_governorate": [], "by_type": []})
        elif name == "centers":
            base.update({"by_governorate": [], "by_partner": []})
        else:
            base.update({"breakdowns": []})
        return base

    # Metric helpers ------------------------------------------------------------
    def _execute_metric(self, breakdown: str) -> Dict[str, Any]:
        try:
            return execute_metric(
                metric_key=self.registration_metric_key,
                breakdown_by=breakdown or "none",
                time_start=self._time_range["start"],
                time_end=self._time_range["end"],
                filters=[],
                user_ctx=self._user_context,
            )
        except Exception:
            return {"rows": []}

    @staticmethod
    def _default_time_range(months: int) -> Dict[str, str]:
        end = date.today()
        start = end - timedelta(days=max(months, 1) * 30)
        return {"start": start.isoformat(), "end": end.isoformat()}

    @staticmethod
    def _format_month(label: Any) -> Optional[str]:
        if not label:
            return None
        if isinstance(label, str):
            text = label.strip()
            if not text:
                return None
            # Accept YYYY-MM-DD or YYYY-MM strings
            if len(text) >= 7 and text[4] == "-":
                return text[:7]
            return text
        return None

    @staticmethod
    def _normalise_value(value: Any) -> Any:
        if value in (None, "", " "):
            return "Unknown"
        return value

    # Scope helpers -------------------------------------------------------------
    def _build_user_context(self, user) -> Dict[str, Any]:
        partner_ids: List[int] = []
        partner_id = getattr(user, "partner_id", None)
        if partner_id:
            partner_ids.append(partner_id)
        return {
            "user_id": getattr(user, "id", None),
            "partner_ids": partner_ids,
            "roles": [],
        }

    def _describe_scope(self) -> Dict[str, Any]:
        user = self.user
        if getattr(user, "is_superuser", False):
            return {"type": "global"}
        scope: Dict[str, Any] = {
            "type": "scoped",
            "username": getattr(user, "username", None),
        }
        if getattr(user, "partner", None):
            scope["partner"] = {
                "id": getattr(user, "partner_id", None),
                "name": getattr(user.partner, "name", None),
            }
        if getattr(user, "center", None):
            scope["center"] = {
                "id": getattr(user, "center_id", None),
                "name": getattr(user.center, "name", None),
            }
        locations = (
            list(getattr(user, "locations", []).values("id", "name"))
            if hasattr(user, "locations")
            else []
        )
        if locations:
            scope["locations"] = locations
        regions = (
            list(getattr(user, "regions", []).values("id", "name"))
            if hasattr(user, "regions")
            else []
        )
        if regions:
            scope["regions"] = regions
        return scope
