# apps/chat/api.py

from __future__ import annotations
from datetime import date, timedelta
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView

from .ai_service import execute_metric
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
from .chat_tools import GET_METRIC_TOOL  # the function schema dict shown earlier

# (Optional) requests fallback to call your /api/metrics/get_metric/ endpoint
import requests


# --- CSRF-safe SessionAuthentication (optional) ---
class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return  # disable CSRF check for API clients


# ---- tiny service layer to hit your metrics execution ----
def call_metrics_service(payload: Dict[str, Any], request=None) -> Dict[str, Any]:
    """
    Call your metrics engine. Three strategies (first that works wins):

    1) Direct Python function (if you have one): execute_metric(payload)  <-- fastest
    2) Internal HTTP to your existing endpoint /api/metrics/get_metric/
    3) As a last resort, raise a clear error
    """
    # 1) Try direct function import (stable if you add a service later)
    try:
        from student_registration.backends.ai_service import execute_metric  # your own service file
        return execute_metric(payload, user=getattr(request, "user", None))
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

    r = requests.post(url, headers=headers, data=json.dumps(payload), timeout=60)
    r.raise_for_status()
    return r.json()


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

    def _llm_tool_call(self, question: str) -> Dict[str, Any] | None:
        """
        Ask the LLM to produce a single get_metric tool call.
        Returns the parsed tool arguments dict, or None if not available.
        """
        client = OpenAI(api_key=getattr(settings, "OPENAI_API_KEY", None))
        model = getattr(settings, "BMA_CHAT_MODEL", "gpt-4o-mini")

        system_msg = (
            "You are a data assistant for the BMA system. Convert user questions into a single "
            "`get_metric` tool call. Infer time ranges (e.g., last year). Prefer `breakdowns` "
            "array (max 3 dims; include `month` for trends). Map phrases: gender→child_gender_norm, "
            "nationality→child_nationality_name, etc. Add gender/age filters when phrased. "
            "If unsure, metric=mscc_registrations_total and breakdowns=['month']."
        )

        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": question},
        ]

        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=[GET_METRIC_TOOL],
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

    def post(self, request, *args, **kwargs):
        # 1) read NL question
        question = (request.data.get("message") or "").strip()
        if not question:
            return Response({"error": "Missing 'question'."}, status=400)

        # 2) try LLM tool call; fallback to deterministic resolver
        tool_payload = None
        try:
            tool_payload = self._llm_tool_call(question)
        except Exception as e:
            # Do not block the request if LLM is unavailable
            tool_payload = None

        if not tool_payload:
            tool_payload = nl_to_metric_payload(question)
        else:
            tool_payload = sanitize_payload(tool_payload)

        # Ensure required fields exist
        if "metric_key" not in tool_payload or "time_range" not in tool_payload:
            tool_payload = nl_to_metric_payload(question)

        # 3) call metrics service
        try:
            result = call_metrics_service(tool_payload, request=request)
        except requests.HTTPError as http_err:
            return Response(
                {
                    "query": tool_payload,
                    "error": f"Metrics service HTTP error: {http_err.response.status_code}",
                    "details": http_err.response.text,
                },
                status=502,
            )
        except Exception as e:
            return Response(
                {"query": tool_payload, "error": f"Metrics service error: {str(e)}"},
                status=500,
            )

        # 4) craft a short human explanation (optional, lightweight)
        explain = self._summarize(tool_payload, result)

        return Response({"query": tool_payload, "result": result, "explanation": explain})

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

