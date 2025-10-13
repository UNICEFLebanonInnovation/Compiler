import re
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from .nl_config import PHRASE_MAP, METRIC_INTENT

ALLOWED_FIELDS = {
    "month","year","governorate","caza","cadaster",
    "child_gender","child_gender_norm","child_nationality_name",
    "partner_id","center_type","cycle","round_id",
    "education_status","education_program","age_band","age_years"
}

def resolve_time_range(text: str) -> dict:
    today = date.today()
    t = text.lower()
    if "last year" in t:
        start, end = date(today.year-1,1,1), date(today.year,1,1)
    elif "this year" in t:
        start, end = date(today.year,1,1), date(today.year+1,1,1)
    elif m := re.search(r"\b(20\d{2})\b", t):
        yr = int(m.group(1)); start, end = date(yr,1,1), date(yr+1,1,1)
    elif "last 6 months" in t or "past 6 months" in t:
        start, end = today - relativedelta(months=6), today + timedelta(days=1)
    else:
        start, end = today - relativedelta(months=12), today + timedelta(days=1)
    return {"start": start.isoformat(), "end": end.isoformat()}

def pick_metric(text: str) -> str:
    t = text.lower()
    for rule in METRIC_INTENT:
        if any(p in t for p in rule["phrases"]):
            return rule["metric"]
    return "mscc_registrations_total"

def extract_breakdowns(text: str) -> list:
    t = text.lower()
    b = []
    if "trend" in t or "monthly" in t:
        b.append("month")
    tokens = []
    for k, cols in PHRASE_MAP.items():
        if k in t:
            tokens.append(cols[0])  # prefer first mapping
    for col in tokens:
        if col in ALLOWED_FIELDS and col not in b:
            b.append(col)
    return (b or ["month"])[:3]

def extract_filters(text: str) -> list:
    f = []
    t = text.lower()
    # gender
    if any(w in t for w in ["female","girls","women"]):
        f.append({"field":"child_gender_norm","op":"in","value":["F","FEMALE"]})
    if any(w in t for w in ["male","boys","men"]):
        f.append({"field":"child_gender_norm","op":"in","value":["M","MALE"]})
    # age > / < / range
    if m := re.search(r"(?:age\s*>\s*|above\s*)(\d+)", t): f.append({"field":"age_years","op":"gt","value":int(m.group(1))})
    if m := re.search(r"(?:age\s*<\s*|below\s*)(\d+)", t): f.append({"field":"age_years","op":"lt","value":int(m.group(1))})
    if m := re.search(r"age\s*(\d+)\s*-\s*(\d+)", t):
        a,b = int(m.group(1)), int(m.group(2))
        f += [{"field":"age_years","op":"gte","value":a},{"field":"age_years","op":"lte","value":b}]
    return f

def sanitize_payload(p: dict) -> dict:
    b = p.get("breakdowns") or []
    p["breakdowns"] = [x for x in b if x in ALLOWED_FIELDS][:3]
    if "breakdown_by" in p and p["breakdown_by"] not in ALLOWED_FIELDS:
        p["breakdown_by"] = "month"
    allowed_ops = {"=", "in", "between"}
    clean_filters = []
    for f in p.get("filters", []):
        field = f.get("field")
        op = f.get("op")
        if field in ALLOWED_FIELDS and op in allowed_ops:
            clean_filters.append(f)
    p["filters"] = clean_filters
    return p

def nl_to_metric_payload(text: str) -> dict:
    payload = {
        "metric_key": pick_metric(text),
        "time_range": resolve_time_range(text),
        "breakdowns": extract_breakdowns(text),
        "filters": extract_filters(text),
    }
    return sanitize_payload(payload)
