import os
import pathlib
import sys
from types import SimpleNamespace

import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

django = pytest.importorskip("django")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
try:
    django.setup()
except Exception:  # pragma: no cover - skip if settings are unavailable
    pytest.skip("Django settings unavailable", allow_module_level=True)

from student_registration.backends import ai_service  # noqa: E402  pylint: disable=wrong-import-position


class _CursorStub:
    def __init__(self):
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params):
        self.executions.append((sql, params))

    def fetchall(self):
        return [(100,)]


class _ConnectionStub:
    def __init__(self):
        self.cursor_stub = _CursorStub()

    def cursor(self):
        # always return the same stub so tests can inspect the last execution
        return self.cursor_stub


@pytest.fixture
def stub_metric(monkeypatch):
    metric = SimpleNamespace(
        key="mscc_registrations_total",
        value_column="value",
        allowed_breakdowns=["none", "month"],
        allowed_filters=["governorate", "age_years", "partner_id"],
        default_time_column="month",
        rounding=1,
        min_sample_size=0,
        unit="registrations",
        sql_view="mv_mscc_registrations_monthly",
        meta={},
    )

    class _Manager:
        def get(self, **kwargs):  # type: ignore[override]
            assert kwargs.get("key") == metric.key
            return metric

    monkeypatch.setattr(ai_service, "Metric", SimpleNamespace(objects=_Manager()))
    return metric


@pytest.fixture
def stub_connection(monkeypatch):
    conn = _ConnectionStub()
    monkeypatch.setattr(ai_service, "connection", conn)
    return conn


def test_execute_metric_supports_comparison_filters(stub_metric, stub_connection):
    result = ai_service.execute_metric(
        metric_key=stub_metric.key,
        breakdown_by="none",
        time_start="2024-01-01",
        time_end="2024-02-01",
        filters=[
            {"field": "age_years", "op": ">", "value": 10},
            {"field": "age_years", "op": "between", "value": [5, 12]},
            {"field": "governorate", "op": "in", "value": ["Beirut", "Mount Lebanon"]},
            {"field": "partner_id", "op": "not in", "value": [101, 202]},
        ],
        user_ctx={},
    )

    sql, params = stub_connection.cursor_stub.executions[-1]
    assert "age_years > %s" in sql
    assert "age_years BETWEEN %s AND %s" in sql
    assert "governorate IN (%s, %s)" in sql
    assert "partner_id NOT IN (%s, %s)" in sql
    # verify parameter ordering: time bounds, comparison, between, IN list
    from datetime import date as _date  # local import to avoid global dependency

    assert params[0] == _date(2024, 1, 1)
    assert params[1] == _date(2024, 2, 1)
    assert params[2] == 10
    assert params[3:5] == [5, 12]
    assert params[5:7] == ["Beirut", "Mount Lebanon"]
    assert params[7:] == [101, 202]
    assert result["total"] == 100
