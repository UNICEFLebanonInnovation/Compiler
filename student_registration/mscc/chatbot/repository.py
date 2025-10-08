"""Data aggregation helpers for the BMA chatbot."""
from __future__ import annotations

import re
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, Iterable, List, Sequence, Tuple

from django.apps import apps
from django.db import DatabaseError, connection, models
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
        try:
            if self._views_available:
                return self._registration_records_from_views()
        except Exception:
            pass
        registrations_list = list(qs)
        return [self._serialise_registration(registration) for registration in registrations_list]

    # View-backed registration helpers ----------------------------------------
    @cached_property
    def _views_available(self) -> bool:
        return self._view_exists("vw_mscc_child")

    def _registration_records_from_views(self) -> List[Dict[str, Any]]:
        columns = self._get_view_columns("vw_mscc_child")
        if not columns:
            raise DatabaseError("vw_mscc_child view has no columns")

        where, params = self._build_view_scope_filters(columns)
        rows = self._fetch_view_rows("vw_mscc_child", where=where, params=params)
        if not rows:
            return []

        registration_ids = [
            reg_id
            for reg_id in (self._extract_registration_id(row, columns) for row in rows)
            if reg_id is not None
        ]
        services = self._services_from_view(registration_ids)

        for row in rows:
            reg_id = self._extract_registration_id(row, columns)
            row["services"] = services.get(reg_id, {})
        return rows

    def _services_from_view(self, registration_ids: List[int]) -> Dict[int, Dict[str, List[Dict[str, Any]]]]:
        columns = self._get_view_columns("vw_mscc_data")
        if not columns:
            return {}

        where, params = self._build_view_scope_filters(columns)
        registration_column = self._identify_registration_column(columns)
        params = list(params)
        if registration_column and registration_ids:
            placeholders = ", ".join(["%s"] * len(registration_ids))
            where = list(where)
            where.append(f"{registration_column} IN ({placeholders})")
            params.extend(registration_ids)

        rows = self._fetch_view_rows("vw_mscc_data", where=where, params=params)
        if not rows:
            return {}

        grouped: Dict[int, Dict[str, List[Dict[str, Any]]]] = defaultdict(lambda: defaultdict(list))
        category_column = self._identify_service_category_column(columns)
        for row in rows:
            reg_id = self._extract_registration_id(row, columns)
            if reg_id is None:
                continue
            category_value = row.get(category_column) if category_column else None
            key = self._service_bucket_key(category_value)
            grouped[reg_id][key].append(row)

        return {
            reg_id: {bucket: list(entries) for bucket, entries in buckets.items()}
            for reg_id, buckets in grouped.items()
        }

    def _view_exists(self, view_name: str) -> bool:
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM {view_name} WHERE 1=0")
        except DatabaseError:
            return False
        return True

    def _get_view_columns(self, view_name: str) -> List[str]:
        cache_key = getattr(self, "_view_columns_cache", None)
        if cache_key is None:
            self._view_columns_cache = {}
        if view_name in self._view_columns_cache:
            return self._view_columns_cache[view_name]
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT * FROM {view_name} WHERE 1=0")
                columns = [col[0] for col in cursor.description]
        except DatabaseError:
            columns = []
        self._view_columns_cache[view_name] = columns
        return columns

    def _build_view_scope_filters(self, columns: Sequence[str]) -> Tuple[List[str], List[Any]]:
        where: List[str] = []
        params: List[Any] = []
        user = self.user
        if getattr(user, "is_superuser", False):
            return where, params

        if getattr(user, "partner_id", None) and "partner_id" in columns:
            where.append("partner_id = %s")
            params.append(user.partner_id)

        if getattr(user, "center_id", None) and "center_id" in columns:
            where.append("center_id = %s")
            params.append(user.center_id)
        else:
            location_ids = self._user_location_ids(user)
            if location_ids:
                location_filters = []
                location_tuple = tuple(location_ids)
                if "governorate_id" in columns:
                    location_filters.append("governorate_id IN %s")
                if "caza_id" in columns:
                    location_filters.append("caza_id IN %s")
                if "cadaster_id" in columns:
                    location_filters.append("cadaster_id IN %s")
                if location_filters:
                    where.append("(" + " OR ".join(location_filters) + ")")
                    params.extend([location_tuple] * len(location_filters))

        region_ids = self._user_region_ids(user)
        if region_ids and "governorate_id" in columns:
            where.append("governorate_id IN %s")
            params.append(tuple(region_ids))

        return where, params

    def _fetch_view_rows(
        self,
        view_name: str,
        *,
        where: Sequence[str] | None = None,
        params: Sequence[Any] | None = None,
    ) -> List[Dict[str, Any]]:
        sql = f"SELECT * FROM {view_name}"
        if where:
            sql += " WHERE " + " AND ".join(where)
        params = list(params or [])
        try:
            with connection.cursor() as cursor:
                cursor.execute(sql, params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]
        except DatabaseError as exc:
            raise exc

    @staticmethod
    def _extract_registration_id(row: Dict[str, Any], columns: Sequence[str]) -> int | None:
        for candidate in ("registration_id", "registration", "registry_id", "id"):
            if candidate in columns:
                value = row.get(candidate)
                if value is None:
                    continue
                if isinstance(value, int):
                    return value
                if isinstance(value, (str, Decimal)):
                    try:
                        return int(float(value))
                    except (TypeError, ValueError):
                        continue
        return None

    @staticmethod
    def _identify_registration_column(columns: Sequence[str]) -> str | None:
        for candidate in ("registration_id", "registration", "registry_id", "id"):
            if candidate in columns:
                return candidate
        return None

    @staticmethod
    def _identify_service_category_column(columns: Sequence[str]) -> str | None:
        for candidate in ("service_model", "service_type", "service_category", "table_name", "service_name"):
            if candidate in columns:
                return candidate
        return None

    def _service_bucket_key(self, value: Any) -> str:
        if not value:
            return "services"
        if isinstance(value, str):
            return self._to_snake_case(value)
        return str(value)

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

    # Serialisation helpers -----------------------------------------------------
    def _serialise_registration(self, registration: Registration) -> Dict[str, Any]:
        data = self._serialise_model_instance(registration)
        data["services"] = self._serialise_registration_services(registration.id)
        return data

    def _serialise_registration_services(self, registration_id: int) -> Dict[str, Any]:
        services: Dict[str, Any] = {}
        for model in self._service_models:
            key = self._service_key(model)
            queryset = model.objects.filter(registration_id=registration_id)
            services[key] = self._serialise_queryset(queryset)
        return services

    def _serialise_queryset(self, queryset: Iterable[models.Model]) -> List[Dict[str, Any]]:
        return [self._serialise_model_instance(instance) for instance in queryset]

    def _serialise_model_instance(self, instance: models.Model) -> Dict[str, Any]:
        data: Dict[str, Any] = {}
        for field in instance._meta.get_fields():
            if field.auto_created and not field.concrete:
                continue

            name = field.name
            value = getattr(instance, name)

            if isinstance(field, models.ManyToManyField):
                ids = list(value.values_list("id", flat=True)) if value is not None else []
                labels = [str(obj) for obj in value.all()] if value is not None else []
                data[name] = ids
                data[f"{name}_labels"] = labels
            elif isinstance(field, models.ForeignKey):
                data[name] = value.pk if value else None
                data[f"{name}_label"] = str(value) if value else None
            else:
                data[name] = self._serialise_value(value)
        return data

    @cached_property
    def _service_models(self) -> List[models.Model]:
        mscc_config = apps.get_app_config("mscc")
        models_with_registration: List[models.Model] = []
        for model in mscc_config.get_models():
            if model is Registration:
                continue
            for field in model._meta.get_fields():
                if (
                    isinstance(field, models.ForeignKey)
                    and field.concrete
                    and not field.auto_created
                    and field.related_model is Registration
                ):
                    models_with_registration.append(model)
                    break
        return models_with_registration

    @staticmethod
    def _service_key(model: models.Model) -> str:
        return BMAInsightsRepository._to_snake_case(model.__name__)

    @staticmethod
    def _to_snake_case(name: str) -> str:
        name = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
        name = re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", name)
        return name.lower()

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
