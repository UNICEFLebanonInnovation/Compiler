import pathlib
import sys

import pytest

pytest.importorskip("dateutil")

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from student_registration.backends import nl_resolver


def test_extract_filters_interprets_age_queries():
    filters = nl_resolver.extract_filters("Show girls age 5-12 above 10")
    ops = {(f["field"], f["op"]) for f in filters}
    assert ("child_gender_norm", "in") in ops
    assert ("age_years", ">") in ops
    assert any(f["op"] == "between" for f in filters if f["field"] == "age_years")


def test_sanitize_payload_keeps_advanced_operations():
    payload = {
        "filters": [
            {"field": "age_years", "op": ">", "value": 12},
            {"field": "age_years", "op": "between", "value": [5, 10]},
            {"field": "partner_id", "op": "not in", "value": [1, 2]},
            {"field": "governorate", "op": "like", "value": "BEI%"},
        ],
        "breakdowns": ["month", "governorate"],
    }

    sanitised = nl_resolver.sanitize_payload(payload)
    assert [f["op"] for f in sanitised["filters"]] == [">", "between", "not in", "like"]
