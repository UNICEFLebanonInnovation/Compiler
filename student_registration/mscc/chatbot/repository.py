"""Data aggregation helpers for the BMA chatbot."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List

from django.db.models import Q, QuerySet
from django.utils import timezone
from django.utils.functional import cached_property

from student_registration.mscc.models import Registration


class BMAInsightsRepository:
    """Aggregate MSCC/BMA data for natural-language insights."""

    def __init__(self, user):
        self.user = user

    # QuerySets -----------------------------------------------------------------
    @cached_property
    def registrations(self) -> QuerySet:
        qs = Registration.objects.filter(deleted=False)
        return self._apply_registration_scope(qs)

    # Public API ----------------------------------------------------------------
    def build_snapshot(self) -> Dict[str, Any]:
        """Build a JSON-serialisable snapshot of the BMA dataset."""
        qs = self.registrations
        records = self._registration_records(qs)

        snapshot: Dict[str, Any] = {
            "generated_at": timezone.now().isoformat(),
            "scope": self._describe_scope(),
            "registrations": {
                "total": len(records),
                "records": records,
            },
        }
        return snapshot

    # Registration helpers ------------------------------------------------------
    def _registration_records(self, qs: QuerySet) -> List[Dict[str, Any]]:
        fields = (
            "id",
            "registration_date",
            "type",
            "child__first_name",
            "child__last_name",
            "child__gender",
            "child__nationality__name",
            "partner__name",
            "center__name",
            "round__name",
            "round__year",
        )
        rows = qs.values(*fields)

        records: List[Dict[str, Any]] = []
        for row in rows:
            first_name = row.get("child__first_name") or ""
            last_name = row.get("child__last_name") or ""
            full_name = " ".join(part for part in [first_name.strip(), last_name.strip()] if part).strip() or None

            records.append(
                {
                    "id": row["id"],
                    "registration_date": self._serialise_value(row.get("registration_date")),
                    "package_type": row.get("type"),
                    "child_name": full_name,
                    "child_gender": row.get("child__gender"),
                    "child_nationality": row.get("child__nationality__name"),
                    "partner": row.get("partner__name"),
                    "center": row.get("center__name"),
                    "round": row.get("round__name"),
                    "year": row.get("round__year"),
                }
            )

        return records
    # Scope helpers -------------------------------------------------------------
    def _apply_registration_scope(self, qs: QuerySet) -> QuerySet:
        user = self.user
        if user.is_superuser:
            return qs
        if getattr(user, "partner_id", None):
            qs = qs.filter(partner_id=user.partner_id)
        if getattr(user, "center_id", None):
            qs = qs.filter(center_id=user.center_id)
        else:
            location_ids = self._user_location_ids(user)
            if location_ids:
                location_filter = (
                    Q(center__governorate_id__in=location_ids)
                    | Q(center__caza_id__in=location_ids)
                    | Q(center__cadaster_id__in=location_ids)
                )
                qs = qs.filter(location_filter)
        region_ids = self._user_region_ids(user)
        if region_ids:
            qs = qs.filter(center__governorate_id__in=region_ids)
        return qs

    def _describe_scope(self) -> Dict[str, Any]:
        user = self.user
        if user.is_superuser:
            return {"type": "global"}
        scope: Dict[str, Any] = {"type": "scoped", "username": getattr(user, "username", None)}
        if getattr(user, "partner", None):
            scope["partner"] = {"id": user.partner_id, "name": getattr(user.partner, "name", None)}
        if getattr(user, "center", None):
            scope["center"] = {"id": user.center_id, "name": getattr(user.center, "name", None)}
        locations = list(getattr(user, "locations", []).values("id", "name")) if hasattr(user, "locations") else []
        if locations:
            scope["locations"] = locations
        regions = list(getattr(user, "regions", []).values("id", "name")) if hasattr(user, "regions") else []
        if regions:
            scope["regions"] = regions
        return scope

    @staticmethod
    def _user_location_ids(user) -> List[int]:
        if hasattr(user, "locations"):
            return list(user.locations.values_list("id", flat=True))
        return []

    @staticmethod
    def _user_region_ids(user) -> List[int]:
        if hasattr(user, "regions"):
            return list(user.regions.values_list("id", flat=True))
        return []

    @staticmethod
    def _serialise_value(value: Any) -> Any:
        if isinstance(value, datetime):
            return value.isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, (list, tuple)):
            return [BMAInsightsRepository._serialise_value(item) for item in value]
        return value
