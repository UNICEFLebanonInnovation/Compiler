"""Data aggregation helpers for the BMA chatbot."""
from __future__ import annotations

from datetime import date
from typing import Any, Dict, List, Optional, Sequence

from django.db.models import Count, Max, Q, QuerySet
from django.db.models.functions import TruncMonth
from django.utils import timezone
from django.utils.functional import cached_property

from student_registration.locations.models import Center
from student_registration.mscc.models import Registration
from student_registration.schools.models import School


class BMAInsightsRepository:
    """Aggregate MSCC/BMA data for natural-language insights."""

    def __init__(
        self,
        user,
        *,
        age_min: Optional[int] = None,
        age_max: Optional[int] = None,
    ):
        self.user = user
        self.age_min = self._normalise_age_filter(age_min)
        self.age_max = self._normalise_age_filter(age_max)
        if (
            self.age_min is not None
            and self.age_max is not None
            and self.age_min > self.age_max
        ):
            raise ValueError("age_min cannot be greater than age_max.")

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
        qs = self._apply_registration_scope(qs)
        return self._apply_age_filter(qs)

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
        snapshot = {
            "total": qs.count(),
            "last_modified": last_modified.isoformat() if last_modified else None,
            "records": self._registration_records(qs),
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
        }
        return snapshot

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

    def _registration_records(self, qs: QuerySet) -> List[Dict[str, Any]]:
        records: List[Dict[str, Any]] = []
        today = self._current_local_date()
        record_qs = qs.order_by("-modified", "-created")
        for registration in record_qs:
            child = getattr(registration, "child", None)
            partner = getattr(registration, "partner", None)
            center = getattr(registration, "center", None)
            round_obj = getattr(registration, "round", None)
            age = None
            if child is not None:
                age = self._age_from_components(
                    getattr(child, "birthday_year", None),
                    getattr(child, "birthday_month", None),
                    getattr(child, "birthday_day", None),
                    today=today,
                )
            records.append(
                {
                    "id": registration.id,
                    "child_name": self._child_name(child),
                    "child_age": age,
                    "child_gender": self._normalise_value(
                        getattr(child, "gender", None)
                    ),
                    "partner": self._normalise_value(getattr(partner, "name", None)),
                    "center": self._normalise_value(getattr(center, "name", None)),
                    "round": self._normalise_value(getattr(round_obj, "name", None)),
                    "package_type": self._normalise_value(getattr(registration, "type", None)),
                    "registration_date": (
                        registration.registration_date.isoformat()
                        if getattr(registration, "registration_date", None)
                        else None
                    ),
                }
            )
        return records

    @staticmethod
    def _child_name(child) -> str:
        if child is None:
            return "Unknown"
        parts = [
            getattr(child, "first_name", None),
            getattr(child, "last_name", None),
        ]
        name = " ".join(part for part in parts if part)
        if name:
            return name
        fallback = getattr(child, "mother_fullname", None) or getattr(
            child, "father_name", None
        )
        return fallback or "Unknown"

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

    def _apply_age_filter(self, qs: QuerySet) -> QuerySet:
        if self.age_min is None and self.age_max is None:
            return qs

        today = self._current_local_date()
        ids: List[int] = []
        for reg_id, year, month, day in qs.values_list(
            "id",
            "child__birthday_year",
            "child__birthday_month",
            "child__birthday_day",
        ):
            age = self._age_from_components(year, month, day, today=today)
            if age is None:
                continue
            if self.age_min is not None and age < self.age_min:
                continue
            if self.age_max is not None and age > self.age_max:
                continue
            ids.append(reg_id)

        return qs.filter(id__in=ids)

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
    def _normalise_age_filter(value: Optional[int | str]) -> Optional[int]:
        if value in (None, ""):
            return None
        try:
            age = int(value)
        except (TypeError, ValueError) as exc:
            raise ValueError("Age filters must be integers.") from exc
        if age < 0:
            raise ValueError("Age filters cannot be negative.")
        return age

    @staticmethod
    def _age_from_components(
        year: Any,
        month: Any,
        day: Any,
        *,
        today: date | None = None,
    ) -> Optional[int]:
        try:
            year_int = int(year)
            month_int = int(month)
            day_int = int(day)
        except (TypeError, ValueError):
            return None
        if not (1 <= month_int <= 12 and 1 <= day_int <= 31):
            return None
        if year_int <= 0:
            return None
        try:
            birthdate = date(year_int, month_int, day_int)
        except ValueError:
            return None
        if today is None:
            today = BMAInsightsRepository._current_local_date()
        age = today.year - birthdate.year - (
            (today.month, today.day) < (birthdate.month, birthdate.day)
        )
        return max(age, 0)

    @staticmethod
    def _current_local_date() -> date:
        now = timezone.now()
        if timezone.is_naive(now):
            return now.date()
        return timezone.localdate(now)
