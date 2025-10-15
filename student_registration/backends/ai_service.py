# apps/metrics/service.py
from datetime import datetime

from django.db import connection

from .models import Metric

ALLOWED_OPS = {"=", "in", "between"}

def _normalize_time_value(value, *, column_type: str):
    """Normalize values used for comparisons against the time column."""

    if column_type == "year":
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            value = value.strip()
            if not value:
                raise ValueError("Empty time value")
            if value.isdigit():
                return int(value)
            try:
                return datetime.fromisoformat(value).year
            except ValueError as exc:
                raise ValueError(f"Invalid year value: {value}") from exc
        raise ValueError(f"Unsupported type for year value: {type(value)!r}")

    return value


def execute_metric(*, metric_key: str, breakdown_by: str = "none",
                   time_start: str, time_end: str, filters: list, user_ctx: dict) -> dict:
    m = Metric.objects.get(key=metric_key)

    time_column_type = (m.meta or {}).get("time_column_type", "date")

    # implicit scoping example
    implicit_filters = []
    if user_ctx.get("partner_ids"):
        implicit_filters.append({"field": "partner_id", "op": "in", "value": user_ctx["partner_ids"]})

    if breakdown_by != "none" and breakdown_by not in m.allowed_breakdowns:
        raise PermissionError("Breakdown not allowed")

    for f in filters + implicit_filters:
        if f["field"] not in m.allowed_filters and f["field"] != m.default_time_column:
            raise PermissionError(f"Filter '{f['field']}' not allowed")
        if f["op"] not in ALLOWED_OPS:
            raise PermissionError("Operator not allowed")

    select = f"SUM({m.value_column}) AS value"
    group = ""
    if breakdown_by != "none":
        select = f"{breakdown_by}, SUM({m.value_column}) AS value"
        group = f" GROUP BY {breakdown_by} ORDER BY value DESC"

    where = [f"{m.default_time_column} >= %s", f"{m.default_time_column} < %s"]
    params = [
        _normalize_time_value(time_start, column_type=time_column_type),
        _normalize_time_value(time_end, column_type=time_column_type),
    ]

    def add_filter(f):
        def normalize(v):
            if f["field"] == m.default_time_column:
                return _normalize_time_value(v, column_type=time_column_type)
            return v

        if f["op"] == "=":
            where.append(f"{f['field']} = %s")
            params.append(normalize(f["value"]))
        elif f["op"] == "in":
            ph = ", ".join(["%s"] * len(f["value"]))
            where.append(f"{f['field']} IN ({ph})")
            params.extend(normalize(v) for v in f["value"])
        elif f["op"] == "between":
            where.append(f"{f['field']} BETWEEN %s AND %s")
            start, end = f["value"]
            params.extend([normalize(start), normalize(end)])

    for f in filters + implicit_filters:
        add_filter(f)

    sql = f"SELECT {select} FROM {m.sql_view} WHERE {' AND '.join(where)}{group}"

    with connection.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    # simple privacy guard
    rounding = max(m.rounding or 1, 1)

    def r(v): return int(round(v / rounding) * rounding)

    if breakdown_by == "none":
        total = rows[0][0] if rows else 0
        if total < m.min_sample_size:
            raise PermissionError("Cohort too small")
        return {"metric_key": m.key, "unit": m.unit, "total": r(total),
                "breakdown_by": "none", "rows": []}

    out = []
    for label, val in rows:
        if val >= m.min_sample_size:
            out.append({"label": str(label), "value": r(val)})
    return {"metric_key": m.key, "unit": m.unit, "total": sum(x["value"] for x in out),
            "breakdown_by": breakdown_by, "rows": out[:100]}
