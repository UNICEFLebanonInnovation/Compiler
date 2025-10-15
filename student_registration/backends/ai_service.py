# apps/metrics/service.py
from __future__ import annotations

from datetime import datetime, date
from typing import Any, Dict, List

from django.db import connection

from .models import Metric

ALLOWED_OPS = {"=", "in", "between"}


def _normalize_time_value(value: Any, *, column_type: str):
    """
    Normalize values used for comparisons against the time column.

    column_type:
      - "year": compare as INT (e.g., 2023)
      - "date": compare as DATE (Python date object)
      - anything else: pass-through (string/number)
    """
    if column_type == "year":
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            v = value.strip()
            if not v:
                raise ValueError("Empty time value")
            if v.isdigit():
                return int(v)
            # ISO date -> take year
            try:
                return datetime.fromisoformat(v).year
            except ValueError as exc:
                raise ValueError(f"Invalid year value: {value}") from exc
        if isinstance(value, date):
            return value.year
        raise ValueError(f"Unsupported type for year value: {type(value)!r}")

    if column_type == "date":
        if isinstance(value, date):
            return value
        if isinstance(value, str):
            v = value.strip()
            if not v:
                raise ValueError("Empty time value")
            # Accept YYYY-MM-DD or YYYY-MM or YYYY
            # Prefer full ISO first
            fmt_try = [None, "%Y-%m-%d", "%Y-%m", "%Y"]
            # datetime.fromisoformat covers full ISO; fallback to strptime patterns
            try:
                return datetime.fromisoformat(v).date()
            except ValueError:
                pass
            for fmt in fmt_try[1:]:
                try:
                    if fmt == "%Y":
                        return date(int(v), 1, 1)
                    return datetime.strptime(v, fmt).date()
                except ValueError:
                    continue
            raise ValueError(f"Invalid date value: {value}")
        # leave numbers alone (unix ts support is out of scope here)
        return value

    # default passthrough
    return value


def execute_metric(
    *,
    metric_key: str,
    breakdown_by: str = "none",
    time_start: str,
    time_end: str,
    filters: List[Dict[str, Any]],
    user_ctx: Dict[str, Any],
) -> dict:
    m = Metric.objects.get(key=metric_key)

    # Detect time column type:
    # - explicit override via metric.meta["time_column_type"]
    # - otherwise infer: if default_time_column == "year" -> "year", else "date"
    time_column_type = (m.meta or {}).get("time_column_type")
    if not time_column_type:
        time_column_type = "year" if (m.default_time_column or "").lower() == "year" else "date"

    # Implicit scoping example
    implicit_filters: List[Dict[str, Any]] = []
    if user_ctx.get("partner_ids"):
        implicit_filters.append(
            {"field": "partner_id", "op": "in", "value": user_ctx["partner_ids"]}
        )

    # Guard: breakdown allowed?
    if breakdown_by != "none" and breakdown_by not in (m.allowed_breakdowns or []):
        raise PermissionError("Breakdown not allowed")

    # Guard: filters allowed?
    for f in filters + implicit_filters:
        if f["field"] not in (m.allowed_filters or []) and f["field"] != m.default_time_column:
            raise PermissionError(f"Filter '{f['field']}' not allowed")
        if f["op"] not in ALLOWED_OPS:
            raise PermissionError("Operator not allowed")

    # SELECT / GROUP BY
    select = f"SUM({m.value_column}) AS value"
    group_clause = ""
    if breakdown_by != "none":
        select = f"{breakdown_by}, SUM({m.value_column}) AS value"
        group_clause = f" GROUP BY {breakdown_by} ORDER BY value DESC"

    # Time WHERE — use typed params (ints for year, date objects for date)
    where = [f"{m.default_time_column} >= %s", f"{m.default_time_column} < %s"]
    params: List[Any] = [
        _normalize_time_value(time_start, column_type=time_column_type),
        _normalize_time_value(time_end, column_type=time_column_type),
    ]

    # Extra filters
    def add_filter(f: Dict[str, Any]):
        def normalize(v):
            if f["field"] == m.default_time_column:
                return _normalize_time_value(v, column_type=time_column_type)
            # If the filter field itself is known to be a year/date in your schema,
            # you can add per-field normalization here as needed.
            return v

        op = f["op"]
        field = f["field"]
        val = f["value"]

        if op == "=":
            where.append(f"{field} = %s")
            params.append(normalize(val))

        elif op == "in":
            if not isinstance(val, (list, tuple)) or len(val) == 0:
                # Avoid invalid SQL like IN ()
                where.append("1=0")
            else:
                ph = ", ".join(["%s"] * len(val))
                where.append(f"{field} IN ({ph})")
                params.extend(normalize(v) for v in val)

        elif op == "between":
            if not isinstance(val, (list, tuple)) or len(val) != 2:
                raise ValueError("between expects [start, end]")
            start, end = val
            where.append(f"{field} BETWEEN %s AND %s")
            params.extend([normalize(start), normalize(end)])

    for f in filters + implicit_filters:
        add_filter(f)

    sql = f"SELECT {select} FROM {m.sql_view} WHERE {' AND '.join(where)}{group_clause}"

    with connection.cursor() as cur:
        cur.execute(sql, params)
        rows = cur.fetchall()

    # Privacy guard / rounding
    rounding = max(m.rounding or 1, 1)
    def r(v): return int(round(v / rounding) * rounding)

    if breakdown_by == "none":
        total = rows[0][0] if rows else 0
        if total < (m.min_sample_size or 0):
            raise PermissionError("Cohort too small")
        return {
            "metric_key": m.key,
            "unit": m.unit,
            "total": r(total),
            "breakdown_by": "none",
            "rows": [],
        }

    out = []
    for label, val in rows:
        if val >= (m.min_sample_size or 0):
            out.append({"label": str(label), "value": r(val)})

    return {
        "metric_key": m.key,
        "unit": m.unit,
        "total": sum(x["value"] for x in out),
        "breakdown_by": breakdown_by,
        "rows": out[:100],
    }
