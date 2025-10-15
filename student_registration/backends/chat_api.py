# apps/chat/api.py

from __future__ import annotations
from datetime import date, datetime, timedelta
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .ai_service import execute_metric, ALLOWED_OPS
from .models import Metric

import json
from typing import Any, Dict, List

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.response import Response
from openai import OpenAI
from django.conf import settings

# If you use SessionAuthentication and got CSRF 403s before, keep this simple stack:
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

# Our helpers (created earlier)
from .nl_resolver import nl_to_metric_payload, sanitize_payload
from .chat_tools import build_get_metric_tool  # dynamic tool schema
from .similarity import MetricSimilarityIndex

# (Optional) requests fallback to call your /api/metrics/get_metric/ endpoint
import requests


# --- CSRF-safe SessionAuthentication (optional) ---
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # disable CSRF check for API clients


# ---- tiny service layer to hit your metrics execution ----
def _build_user_context(request) -> Dict[str, Any]:
    user = getattr(request, "user", None)
    if not user:
        return {}

    partner_ids_attr = getattr(user, "partner_ids", None)
    partner_ids = []
    if callable(partner_ids_attr):
        try:
            partner_ids = partner_ids_attr()
        except TypeError:
            partner_ids = []
    elif partner_ids_attr is not None:
        partner_ids = partner_ids_attr

    if partner_ids is None:
        partner_ids = []

    try:
        partner_ids = list(partner_ids)
    except TypeError:
        partner_ids = []

    roles = []
    groups = getattr(user, "groups", None)
    if groups is not None:
        try:
            roles = list(groups.values_list("name", flat=True))
        except Exception:
            roles = [getattr(g, "name", "") for g in groups.all()]

    return {
        "user_id": getattr(user, "id", None),
        "partner_ids": partner_ids,
        "roles": [r for r in roles if r],
    }


def _normalize_year_value(value: Any) -> int:
    """Convert a year-like value (int, ISO date string) into an integer year."""

    if isinstance(value, int):
        return value

    if isinstance(value, str):
        raw = value.strip()
        if not raw:
            raise ValueError("Empty year value")
        if raw.isdigit():
            return int(raw)
        try:
            return datetime.fromisoformat(raw).year
        except ValueError as exc:
            raise ValueError(f"Invalid year value: {value}") from exc

    raise ValueError(f"Unsupported type for year value: {type(value)!r}")


def _normalize_time_inputs(payload: Dict[str, Any]) -> None:
    """Normalize time range and filters according to the metric's time column."""

    metric_key = payload.get("metric_key")
    if not metric_key:
        return

    try:
        metric = Metric.objects.get(key=metric_key)
    except Metric.DoesNotExist:
        return

    time_column_type = (metric.meta or {}).get("time_column_type", "date")
    if time_column_type != "year":
        return

    time_range = payload.get("time_range") or {}
    for bound in ("start", "end"):
        value = time_range.get(bound)
        if value not in (None, ""):
            time_range[bound] = _normalize_year_value(value)

    for f in payload.get("filters", []):
        if f.get("field") != metric.default_time_column:
            continue

        op = f.get("op")
        value = f.get("value")

        if op == "between" and isinstance(value, (list, tuple)) and len(value) == 2:
            f["value"] = [
                _normalize_year_value(value[0]),
                _normalize_year_value(value[1]),
            ]
        elif op == "in" and isinstance(value, (list, tuple)):
            f["value"] = [_normalize_year_value(v) for v in value]
        elif op == "=" and value is not None:
            f["value"] = _normalize_year_value(value)


def call_metrics_service(payload: Dict[str, Any], request=None) -> Dict[str, Any]:
    """
    Call your metrics engine. Three strategies (first that works wins):

    1) Direct Python function (if you have one): execute_metric(payload)  <-- fastest
    2) Internal HTTP to your existing endpoint /api/metrics/get_metric/
    3) As a last resort, raise a clear error
    """
    _normalize_time_inputs(payload)

    # 1) Try direct function import (stable if you add a service later)
    try:
        from student_registration.backends.ai_service import execute_metric  # your own service file

        time_range = payload.get("time_range", {})
        start = time_range.get("start")
        end = time_range.get("end")

        if not start or not end:
            raise ValueError("Missing time range for metric execution")

        breakdown_by = payload.get("breakdown_by") or "none"

        return execute_metric(
            metric_key=payload["metric_key"],
            breakdown_by=breakdown_by,
            time_start=start,
            time_end=end,
            filters=payload.get("filters", []),
            user_ctx=_build_user_context(request),
        )
    except Exception:
        pass

    # 2) HTTP fallback
    base = getattr(settings, "BMA_METRICS_BASE_URL", "http://127.0.0.1:8000")
    path = getattr(settings, "BMA_METRICS_PATH", "/api/metrics/get_metric/")
    url = f"{base.rstrip('/')}{path}"

    headers = {"Content-Type": "application/json"}
    # If you require auth, add a token header here (e.g., settings.BMA_API_TOKEN)
    token = getattr(settings, "BMA_API_TOKEN", None)
    if token:
        headers["Authorization"] = f"Token {token}"

    session = requests.Session()

    if request is not None:
        # Reuse the caller's authentication context when available so that
        # SessionAuthentication/BasicAuthentication checks on the internal
        # endpoint succeed. This mirrors a browser request that already has a
        # logged-in session cookie or Authorization header.
        try:
            cookies = getattr(request, "COOKIES", None) or {}
            if cookies:
                session.cookies.update(cookies)
        except Exception:
            pass

        if "Authorization" not in headers:
            auth_header = getattr(request, "META", {}).get("HTTP_AUTHORIZATION")
            if auth_header:
                headers["Authorization"] = auth_header

    r = session.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    return r.json()


# --- Direct metrics execution endpoint ---
class MetricGetView(APIView):
    """Execute a metric request and return aggregated results."""

    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def _validate_filters(self, filters, metric):
        if filters in (None, ""):
            return []
        if not isinstance(filters, list):
            raise ValueError("'filters' must be a list of objects")

        allowed_fields = set(metric.allowed_filters or [])
        cleaned = []
        for item in filters:
            if not isinstance(item, dict):
                raise ValueError("Each filter must be an object")
            field = item.get("field")
            op = item.get("op")
            if not field or not op:
                raise ValueError("Each filter requires 'field' and 'op'")
            if field not in allowed_fields and field != metric.default_time_column:
                raise ValueError(f"Filter field '{field}' is not allowed for this metric")
            if op not in ALLOWED_OPS:
                raise ValueError(f"Operator '{op}' is not permitted")
            cleaned.append({
                "field": field,
                "op": op,
                "value": item.get("value"),
            })
        return cleaned

    def post(self, request, *args, **kwargs):
        if not isinstance(request.data, dict):
            return Response({"error": "Invalid payload."}, status=status.HTTP_400_BAD_REQUEST)

        metric_key = request.data.get("metric_key")
        if not metric_key:
            return Response({"error": "'metric_key' is required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            metric = Metric.objects.get(key=metric_key)
        except Metric.DoesNotExist:
            return Response({"error": f"Unknown metric '{metric_key}'."}, status=status.HTTP_404_NOT_FOUND)

        time_range = request.data.get("time_range") or {}
        start = time_range.get("start")
        end = time_range.get("end")
        if not start or not end:
            return Response(
                {"error": "'time_range.start' and 'time_range.end' are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        breakdown_by = request.data.get("breakdown_by")
        if not breakdown_by:
            breakdowns = request.data.get("breakdowns") or []
            breakdown_by = breakdowns[0] if breakdowns else "none"

        allowed_breakdowns = set(metric.allowed_breakdowns or [])
        if breakdown_by not in (allowed_breakdowns | {"none"}):
            return Response(
                {"error": f"Breakdown '{breakdown_by}' is not allowed for this metric."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            filters = self._validate_filters(request.data.get("filters"), metric)
        except ValueError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            result = execute_metric(
                metric_key=metric_key,
                breakdown_by=breakdown_by or "none",
                time_start=start,
                time_end=end,
                filters=filters,
                user_ctx=_build_user_context(request),
            )
        except PermissionError as exc:
            return Response({"error": str(exc)}, status=status.HTTP_403_FORBIDDEN)
        except Exception as exc:
            return Response({"error": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(result, status=status.HTTP_200_OK)


# --- Tool implementations the orchestrator can execute ---
def tool_list_metrics():
    rows = Metric.objects.all().values(
        "key","label","description","allowed_breakdowns","allowed_filters","default_time_column","unit","tags"
    )
    # Keep payload small
    return list(rows)[:200]

def tool_get_metric(args, user):
    user_ctx = {
        "user_id": user.id,
        "partner_ids": getattr(user, "partner_ids", []),
        "roles": [g.name for g in user.groups.all()],
    }
    return execute_metric(
        metric_key=args["metric_key"],
        breakdown_by=args.get("breakdown_by","none"),
        time_start=args["time_range"]["start"],
        time_end=args["time_range"]["end"],
        filters=args.get("filters", []),
        user_ctx=user_ctx
    )

# --- Default time window logic ---
def default_timerange():
    # last 6 full months ending today (Asia/Beirut local is fine; keep ISO date)
    end = date.today()
    start = end - timedelta(days=180)
    return {"start": start.isoformat(), "end": end.isoformat()}

# --- LLM call using Azure OpenAI or OpenAI ---
# Pseudocode: replace with your client init.
def llm_call(messages, tools):
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.2,
        messages=messages,
        tools=tools,
        tool_choice="auto",
    )
    m = resp.choices[0].message
    # Convert to plain dict we can append to `messages`
    out = {
        "role": "assistant",
        "content": m.content,
        "tool_calls": []
    }
    if getattr(m, "tool_calls", None):
        for tc in m.tool_calls:
            out["tool_calls"].append({
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments,
                }
            })
    return out


# ---- the AskView ----
class AskView(APIView):
    """
    POST /api/chat/ask/
    Body: {"question": "<natural language text>"}

    Returns:
      {
        "query": {metric request we sent},
        "result": {metrics API response},
        "explanation": "...short human summary..."
      }
    """
    authentication_classes = [CsrfExemptSessionAuthentication, SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]  # switch to IsAuthenticated if your UI has login

    def _get_similarity_index(self, metrics: List[Metric]) -> MetricSimilarityIndex | None:
        if not hasattr(self, "_metric_similarity_index"):
            try:
                self._metric_similarity_index = MetricSimilarityIndex(metrics)
            except Exception:
                self._metric_similarity_index = None
        return getattr(self, "_metric_similarity_index", None)

    def _build_similarity_context(self, question: str, metrics: List[Metric]) -> str:
        index = self._get_similarity_index(metrics)
        if not index:
            return ""
        try:
            return index.build_context(question, top_k=3)
        except Exception:
            return ""

    def _suggest_metric_key(self, question: str, metrics: List[Metric]) -> str | None:
        index = self._get_similarity_index(metrics)
        if not index:
            return None
        try:
            match = index.best_match(question)
        except Exception:
            return None
        if not match:
            return None
        return match.metadata.get("metric_key") or match.key

    def _llm_tool_call(self, question: str) -> Dict[str, Any] | None:
        """
        Ask the LLM to produce a single get_metric tool call.
        Returns the parsed tool arguments dict, or None if not available.
        """
        metrics = list(Metric.objects.all())
        if not metrics:
            return None

        tool_schema = build_get_metric_tool(metrics)
        client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
        model = getattr(settings, "BMA_CHAT_MODEL", "gpt-4o-mini")

        system_msg = self._build_system_prompt(metrics)

        similarity_context = self._build_similarity_context(question, metrics)

        messages = [{"role": "system", "content": system_msg}]
        if similarity_context:
            messages.append({"role": "system", "content": similarity_context})
        messages.append({"role": "user", "content": question})

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[tool_schema],
            tool_choice="auto",
            temperature=0.2,
        )

        msg = resp.choices[0].message
        tool_calls = getattr(msg, "tool_calls", None)
        if not tool_calls:
            return None

        # pick the first tool call named get_metric
        for tc in tool_calls:
            if tc.function and tc.function.name == "get_metric":
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}
                return args or None

        return None

    def _build_system_prompt(self, metrics: List[Metric]) -> str:
        lines = [
            "You are a Makani Support data assistant. Your job is to map natural language questions",
            "to a single `get_metric` tool call. Always produce ISO8601 dates (YYYY-MM-DD).",
            "Infer reasonable time ranges (e.g. last 6 months) when the user does not specify any.",
            "Pick at most three breakdowns and include `month` for trend style questions.",
            "Only use filters/breakdowns that exist for the chosen metric."
        ]

        lines.append("Available metrics:")
        for metric in metrics:
            breakdowns = getattr(metric, "allowed_breakdowns", []) or []
            allowed = ", ".join([b for b in breakdowns if b != "none"]) or "none"
            filters = ", ".join(getattr(metric, "allowed_filters", []) or []) or "none"
            lines.append(
                f"- {metric.key}: {metric.label}. Breakdowns: {allowed}. Filters: {filters}"
            )

        lines.append("If unsure choose mscc_registrations_total with breakdowns=['month'].")
        return "\n".join(lines)

    def _normalize_payload(self, payload: Dict[str, Any], metrics: List[Metric]) -> Dict[str, Any]:
        payload = sanitize_payload(payload or {})

        metric_key = payload.get("metric_key") or "mscc_registrations_total"
        payload["metric_key"] = metric_key

        metric = next((m for m in metrics if m.key == metric_key), None)

        time_range = payload.get("time_range") or {}
        start = time_range.get("start")
        end = time_range.get("end")
        if not start or not end:
            time_range = default_timerange()
        payload["time_range"] = time_range

        breakdowns = payload.get("breakdowns") or []
        allowed_breakdowns = list(getattr(metric, "allowed_breakdowns", []) or []) if metric else []
        allowed_breakdowns = [b for b in allowed_breakdowns if b and b != "none"]
        if metric:
            breakdowns = [b for b in breakdowns if b in allowed_breakdowns][:3]
        else:
            breakdowns = breakdowns[:3]
        payload["breakdowns"] = breakdowns

        breakdown_by = payload.get("breakdown_by")
        if breakdown_by not in allowed_breakdowns:
            breakdown_by = breakdowns[0] if breakdowns else "none"
        payload["breakdown_by"] = breakdown_by or "none"

        filters = payload.get("filters") or []
        if metric:
            allowed_filters = set(getattr(metric, "allowed_filters", []) or [])
            filters = [f for f in filters if f.get("field") in allowed_filters]
        payload["filters"] = filters

        return payload

    def _run_orchestrated_call(
        self, question: str, request, metrics: List[Metric]
    ) -> Dict[str, Any] | None:
        if not metrics:
            return None

        tool_schema = build_get_metric_tool(metrics)
        client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
        model = getattr(settings, "BMA_CHAT_MODEL", "gpt-4o-mini")

        system_prompt = self._build_system_prompt(metrics)
        similarity_context = self._build_similarity_context(question, metrics)

        messages = [{"role": "system", "content": system_prompt}]
        if similarity_context:
            messages.append({"role": "system", "content": similarity_context})
        messages.append({"role": "user", "content": question})

        first = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[tool_schema],
            tool_choice="auto",
            temperature=0.2,
        )

        assistant_msg = first.choices[0].message
        tool_calls = getattr(assistant_msg, "tool_calls", None) or []

        if not tool_calls:
            return None

        execution_payload = None
        execution_result = None
        tool_messages = []

        for tc in tool_calls:
            if tc.function and tc.function.name == "get_metric":
                try:
                    args = json.loads(tc.function.arguments or "{}")
                except json.JSONDecodeError:
                    args = {}

                normalized = self._normalize_payload(args, metrics)
                execution_payload = normalized
                execution_result = call_metrics_service(normalized, request=request)
                tool_messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tc.id,
                        "content": json.dumps(
                            {
                                "query": normalized,
                                "result": execution_result,
                            },
                            default=str,
                        ),
                    }
                )

        if execution_payload is None or execution_result is None:
            return None

        assistant_dict = {
            "role": "assistant",
            "content": assistant_msg.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments,
                    },
                }
                for tc in tool_calls
            ],
        }

        follow_up_messages = messages + [assistant_dict] + tool_messages

        second = client.chat.completions.create(
            model=model,
            messages=follow_up_messages,
            temperature=0.3,
        )

        final_content = second.choices[0].message.content or ""

        return {
            "strategy": "orchestrated",
            "query": execution_payload,
            "result": execution_result,
            "explanation": final_content,
        }

    def post(self, request, *args, **kwargs):
        # 1) read NL question
        question = (request.data.get("message") or "").strip()
        if not question:
            return Response({"error": "Missing 'question'."}, status=400)

        # 2) try LLM tool call; fallback to deterministic resolver
        metrics = list(Metric.objects.all())
        if not metrics:
            return Response(
                {"error": "No metrics are configured in the system."},
                status=503,
            )

        orchestrated = None
        try:
            orchestrated = self._run_orchestrated_call(question, request, metrics)
        except Exception:
            orchestrated = None

        if orchestrated:
            return Response(orchestrated)

        tool_payload = nl_to_metric_payload(question)

        suggested_metric = self._suggest_metric_key(question, metrics)
        if suggested_metric:
            tool_payload["metric_key"] = suggested_metric

        if "breakdown_by" not in tool_payload:
            breakdowns = tool_payload.get("breakdowns") or []
            tool_payload["breakdown_by"] = breakdowns[0] if breakdowns else "none"

        normalized_payload = self._normalize_payload(tool_payload, metrics)

        # 3) call metrics service
        try:
            result = call_metrics_service(normalized_payload, request=request)
        except requests.HTTPError as http_err:
            status_code = getattr(getattr(http_err, "response", None), "status_code", None)
            response_text = getattr(getattr(http_err, "response", None), "text", "")
            return Response(
                {
                    "query": normalized_payload,
                    "error": "Metrics service HTTP error",
                    "status_code": status_code,
                    "details": response_text,
                },
                status=502,
            )
        except Exception as e:
            return Response(
                {"query": normalized_payload, "error": f"Metrics service error: {str(e)}"},
                status=500,
            )

        # 4) craft a short human explanation (optional, lightweight)
        explain = self._summarize(normalized_payload, result)

        return Response(
            {
                "strategy": "fallback",
                "query": normalized_payload,
                "result": result,
                "explanation": explain,
            }
        )

    # --- tiny summary for UX; pure Python, no extra OpenAI call ---
    def _summarize(self, q: Dict[str, Any], r: Dict[str, Any]) -> str:
        """
        Builds a 1-line natural language explanation of what was returned.
        """
        metric = q.get("metric_key")
        tr = q.get("time_range", {})
        start, end = tr.get("start"), tr.get("end")
        b = q.get("breakdowns") or ([q["breakdown_by"]] if q.get("breakdown_by") else [])
        btxt = ", ".join(b) if b else "none"
        total = r.get("total") or r.get("value") or r.get("sum")  # depends on your API shape

        base = f"{metric} for {start} → {end} (breakdowns: {btxt})"
        if total is not None:
            return f"{base}. Total: {total}."
        return base + "."


class ChatbotAIView(LoginRequiredMixin, TemplateView):
    """Render the HTML page that hosts the chatbot interface."""

    template_name = "backends/chat_ai.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

