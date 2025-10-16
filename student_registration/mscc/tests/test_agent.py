import os
import pathlib
import sys
from types import SimpleNamespace

import django
import pytest

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

os.environ.setdefault("DATABASE_URL", "sqlite:///test.sqlite3")
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.test")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

from student_registration.backends.models import Metric  # noqa: E402
from student_registration.mscc.chatbot.agent import BMAMetricsAgent  # noqa: E402


@pytest.fixture()
def user(db):
    user_model = get_user_model()
    return user_model.objects.create_user(username="metrics-analyst", password="pwd12345")


@pytest.fixture()
def metric(db):
    return Metric.objects.create(
        key="mscc_registrations_total",
        label="Registrations total",
        description="Total number of active registrations",
        sql_view="mv_mscc_registrations",
        value_column="registration_total",
        allowed_breakdowns=["none", "month", "governorate"],
        allowed_filters=["governorate", "month", "age_years", "child_gender_norm"],
        default_time_column="registration_month",
    )


@pytest.mark.django_db
def test_agent_returns_metric_response(monkeypatch, user, metric):
    def fake_execute_metric(**kwargs):
        assert kwargs["metric_key"] == metric.key
        assert kwargs["breakdown_by"] in {"none", "month", "governorate"}
        return {
            "metric_key": metric.key,
            "unit": "count",
            "total": 42,
            "breakdown_by": kwargs["breakdown_by"],
            "rows": [],
            "generated_at": "2024-05-01T00:00:00Z",
        }

    monkeypatch.setattr(
        "student_registration.mscc.chatbot.agent.execute_metric", fake_execute_metric
    )
    monkeypatch.setattr(
        "student_registration.mscc.chatbot.agent.MetricSimilarityIndex",
        lambda metrics: SimpleNamespace(
            search=lambda *args, **kwargs: [
                SimpleNamespace(
                    key=metric.key,
                    summary="Registrations total",
                    metadata={"metric_key": metric.key, "label": metric.label},
                )
            ]
        ),
    )

    agent = BMAMetricsAgent(user, metrics=[metric])
    response = agent.answer("Show me the registrations trend by month")

    assert response["query"]["metric_key"] == metric.key
    assert response["result"]["total"] == 42
    assert response["selected_metric"]["sql_view"] == metric.sql_view
    assert "Registrations total" in response["explanation"]
    assert response["similarity_suggestions"][0]["metric_key"] == metric.key


@pytest.mark.django_db
def test_agent_preserves_multiple_filters(monkeypatch, user, metric):
    def fake_nl_to_metric_payload(question):
        return {
            "metric_key": metric.key,
            "time_range": {"start": "2024-01-01", "end": "2024-02-01"},
            "breakdowns": ["month"],
            "filters": [
                {"field": "governorate", "op": "in", "value": ["Amman", "Irbid"]},
                {"field": "age_years", "op": ">", "value": 10},
            ],
        }

    captured = {}

    def fake_execute_metric(**kwargs):
        captured["filters"] = kwargs.get("filters", [])
        return {
            "metric_key": metric.key,
            "unit": "count",
            "total": 11,
            "breakdown_by": kwargs.get("breakdown_by", "none"),
            "rows": [],
            "generated_at": "2024-05-01T00:00:00Z",
        }

    monkeypatch.setattr(
        "student_registration.mscc.chatbot.agent.nl_to_metric_payload",
        fake_nl_to_metric_payload,
    )
    monkeypatch.setattr(
        "student_registration.mscc.chatbot.agent.execute_metric", fake_execute_metric
    )
    monkeypatch.setattr(
        "student_registration.mscc.chatbot.agent.MetricSimilarityIndex",
        lambda metrics: SimpleNamespace(search=lambda *args, **kwargs: []),
    )

    agent = BMAMetricsAgent(user, metrics=[metric])
    response = agent.answer("Registrations in Amman above age 10")

    assert [f["field"] for f in response["query"]["filters"]] == [
        "governorate",
        "age_years",
    ]
    assert captured["filters"] == response["query"]["filters"]


@pytest.mark.django_db
def test_agent_rejects_blank_question(user, metric):
    agent = BMAMetricsAgent(user, metrics=[metric])
    with pytest.raises(BMAMetricsAgent.AgentError):
        agent.answer("   ")
