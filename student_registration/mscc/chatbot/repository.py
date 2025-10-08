"""Data aggregation helpers for the BMA chatbot."""
from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Sequence

from django.db.models import Count, Max, Q, QuerySet
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.functional import cached_property

from student_registration.locations.models import Center
from student_registration.mscc.models import Registration
from student_registration.schools.models import School


class BMAInsightsRepository:
    """Aggregate MSCC/BMA data for natural-language insights."""

    def __init__(self, user):
        self.user = user

    # QuerySets -----------------------------------------------------------------
    @cached_property
    def registrations(self) -> QuerySet:
        qs = (
            Registration.objects.filter(deleted=False)
            .select_related(
                "round",
                "partner",
                "center__partner",
                "center__governorate",
                "center__caza",
                "center__cadaster",
                "child",
                "child__nationality",
            )
        )
        return self._apply_registration_scope(qs)

    @cached_property
    def schools(self) -> QuerySet:
        qs = School.objects.filter(is_bma=True, is_closed=False)
        return self._apply_school_scope(qs)

    @cached_property
    def centers(self) -> QuerySet:
        qs = Center.objects.all()
        return self._apply_center_scope(qs)

    # Public API ----------------------------------------------------------------
    def build_snapshot(self) -> Dict[str, Any]:
        """Build a JSON-serialisable snapshot of the BMA dataset."""
        registrations = self.registrations
        schools = self.schools
        centers = self.centers

        snapshot: Dict[str, Any] = {
            "generated_at": timezone.now().isoformat(),
            "scope": self._describe_scope(),
            "registrations": self._registration_snapshot(registrations),
            "schools": self._school_snapshot(schools),
            "centers": self._center_snapshot(centers),
        }
        return snapshot

    # Registration helpers ------------------------------------------------------
    def _registration_snapshot(self, qs: QuerySet) -> Dict[str, Any]:
        last_modified = qs.aggregate(value=Max("modified"))['value']
        total = qs.count()
        snapshot = {
            "total": total,
            "last_modified": last_modified.isoformat() if last_modified else None,
            "by_round": self._counts(
                qs,
                fields=("round__name", "round__year"),
                label_map={"round__name": "round", "round__year": "year"},
            ),
            "by_gender": self._counts(
                qs,
                fields=("child__gender",),
                label_map={"child__gender": "gender"},
            ),
            "by_nationality": self._counts(
                qs,
                fields=("child__nationality__name",),
                label_map={"child__nationality__name": "nationality"},
                limit=10,
            ),
            "by_partner": self._counts(
                qs,
                fields=("partner__name",),
                label_map={"partner__name": "partner"},
                limit=10,
            ),
            "by_package_type": self._counts(
                qs,
                fields=("type",),
                label_map={"type": "package_type"},
            ),
            "by_governorate": self._counts(
                qs,
                fields=("center__governorate__name",),
                label_map={"center__governorate__name": "governorate"},
                limit=10,
            ),
            "monthly_trend": self._monthly_trend(qs, months=12),
            "records": self._registration_records(qs),
        }
        return snapshot

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
            "center__governorate__name",
            "center__caza__name",
            "center__cadaster__name",
            "round__name",
            "round__year",
        )
        rows = (
            qs.select_related(
                "child__nationality",
                "partner",
                "center__governorate",
                "center__caza",
                "center__cadaster",
                "round",
            )
            .values(*fields)
        )

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
                    "governorate": row.get("center__governorate__name"),
                    "district": row.get("center__caza__name"),
                    "cadaster": row.get("center__cadaster__name"),
                    "round": row.get("round__name"),
                    "year": row.get("round__year"),
                }
            )

        return records

    # School helpers ------------------------------------------------------------
    def _school_snapshot(self, qs: QuerySet) -> Dict[str, Any]:
        return {
            "total": qs.count(),
            "by_governorate": self._counts(
                qs,
                fields=("governorate__name",),
                label_map={"governorate__name": "governorate"},
            ),
            "by_type": self._counts(
                qs,
                fields=("type",),
                label_map={"type": "school_type"},
            ),
        }

    # Center helpers ------------------------------------------------------------
    def _center_snapshot(self, qs: QuerySet) -> Dict[str, Any]:
        return {
            "total": qs.count(),
            "by_governorate": self._counts(
                qs,
                fields=("governorate__name",),
                label_map={"governorate__name": "governorate"},
            ),
            "by_partner": self._counts(
                qs,
                fields=("partner__name",),
                label_map={"partner__name": "partner"},
            ),
        }

    # Generic aggregation helpers ----------------------------------------------
    def _counts(
        self,
        qs: QuerySet,
        *,
        fields: Sequence[str],
        label_map: Dict[str, str],
        limit: int | None = None,
    ) -> List[Dict[str, Any]]:
        annotated = (
            qs.values(*fields)
            .annotate(total=Count("id"))
            .order_by("-total")
        )
        if limit:
            annotated = annotated[:limit]

        results: List[Dict[str, Any]] = []
        for row in annotated:
            item = {"count": row["total"]}
            for field in fields:
                label = label_map.get(field, field)
                item[label] = self._normalise_value(row.get(field))
            results.append(item)
        return results

    def _monthly_trend(self, qs: QuerySet, *, months: int = 12) -> List[Dict[str, Any]]:
        trend_qs = (
            qs.filter(registration_date__isnull=False)
            .annotate(month=TruncMonth("registration_date"))
            .values("month")
            .annotate(total=Count("id"))
            .order_by("month")
        )

        points: List[Dict[str, Any]] = []
        for row in trend_qs:
            month = row.get("month")
            if not month:
                continue
            points.append({
                "month": month.strftime("%Y-%m"),
                "registrations": row["total"],
            })

        if months:
            points = points[-months:]
        return points

    @staticmethod
    def _normalise_value(value: Any) -> Any:
        if value in (None, "", " "):
            return "Unknown"
        return value

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

    def _apply_school_scope(self, qs: QuerySet) -> QuerySet:
        user = self.user
        if user.is_superuser:
            return qs
        if getattr(user, "partner_id", None):
            qs = qs.filter(partner_schools__id=user.partner_id)
        location_ids = self._user_location_ids(user)
        if location_ids:
            qs = qs.filter(
                Q(governorate_id__in=location_ids)
                | Q(district_id__in=location_ids)
                | Q(cadaster_id__in=location_ids)
            )
        region_ids = self._user_region_ids(user)
        if region_ids:
            qs = qs.filter(governorate_id__in=region_ids)
        return qs.distinct()

    def _apply_center_scope(self, qs: QuerySet) -> QuerySet:
        user = self.user
        if user.is_superuser:
            return qs
        if getattr(user, "partner_id", None):
            qs = qs.filter(partner_id=user.partner_id)
        location_ids = self._user_location_ids(user)
        if location_ids:
            qs = qs.filter(
                Q(governorate_id__in=location_ids)
                | Q(caza_id__in=location_ids)
                | Q(cadaster_id__in=location_ids)
            )
        region_ids = self._user_region_ids(user)
        if region_ids:
            qs = qs.filter(governorate_id__in=region_ids)
        return qs.distinct()

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
