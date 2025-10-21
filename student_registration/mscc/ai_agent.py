"""Utility helpers for the MSCC health support AI agent."""

from __future__ import annotations

import json
import logging
from typing import List, Sequence

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


class AgentConfigurationError(RuntimeError):
    """Raised when the agent is not configured correctly."""


class AgentAPIError(RuntimeError):
    """Raised when the upstream OpenAI API returns an error."""


class HealthSupportAgent:
    """Simple wrapper around the OpenAI chat completion endpoint."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
    ) -> None:
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        if not self.api_key:
            raise AgentConfigurationError("OpenAI API key is not configured.")

        self.model = model or getattr(settings, "OPENAI_HEALTH_AGENT_MODEL", "gpt-4o-mini")
        self.base_url = base_url or getattr(settings, "OPENAI_API_BASE", "https://api.openai.com/v1")
        self.timeout = timeout or int(getattr(settings, "OPENAI_TIMEOUT", 30))

    def analyze_children(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
    ) -> str:
        """Generate an analysis for the supplied children context."""

        if focus_topics is None:
            focus_topics = self.infer_focus_topics(question)

        messages = self._build_prompt(
            children_context,
            question=question,
            focus_topics=focus_topics,
        )
        return self._request_chat_completion(messages)

    def _build_prompt(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
    ) -> List[dict]:
        summary = json.dumps(children_context, indent=2, default=str)
        system_message = (
            "You are an expert public health analyst supporting the MSCC "
            "(Makani Strategic Child Care) programme."
        )
        user_instructions = (
            "Review the children information and highlight who requires urgent "
            "support or follow-up. Consider age, psychosocial (PSS) services, "
            "health services, attendance history, and other support needs. "
            "Provide actionable recommendations for each child."
        )
        formatting = (
            "Return your response in markdown with the sections 'Priority Cases', "
            "'Watch List', and 'Key Programme Insights'. List each child with "
            "their registration id and a short rationale."
        )

        focus_topics = set(focus_topics or [])
        question_text = (question or "").strip()
        if question_text:
            user_instructions = (
                f"{user_instructions}\n\nFocus specifically on: {question_text}"
            )

        if focus_topics:
            sorted_topics = ", ".join(sorted(focus_topics))
            scope_instruction = (
                "\n\nLimit your assessment strictly to the following domains: "
                f"{sorted_topics}. Do not discuss other programme dimensions "
                "unless they directly influence these focus areas."
            )

            if focus_topics == {"nutrition"}:
                scope_instruction += (
                    " Give detailed nutrition-specific insights, including "
                    "feeding practices, malnutrition risks, and related "
                    "health referrals. Avoid reporting on attendance, PSS, or "
                    "other services unless they materially change the "
                    "nutrition findings."
                )

            user_instructions = f"{user_instructions}{scope_instruction}"

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"{user_instructions}\n\n{formatting}\n\nChildren data:\n{summary}",
            },
        ]
        return messages

    @staticmethod
    def infer_focus_topics(question: str | None) -> set[str]:
        """Derive focus topics from the staff question for prompt tailoring."""

        if not isinstance(question, str):
            return set()

        text = question.lower()
        mapping = {
            "nutrition": {"nutrition"},
            "malnutrition": {"nutrition"},
            "feeding": {"nutrition"},
            "diet": {"nutrition"},
            "health": {"health"},
            "medical": {"health"},
            "attendance": {"attendance"},
            "absent": {"attendance"},
            "psycho": {"pss"},
            "pss": {"pss"},
            "psychosocial": {"pss"},
            "support": {"support"},
            "caregiver": {"support"},
        }

        focus = set()
        for keyword, topics in mapping.items():
            if keyword in text:
                focus.update(topics)

        return focus

    def _request_chat_completion(self, messages: Sequence[dict]) -> str:
        url = f"{self.base_url.rstrip('/')}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": list(messages),
            "temperature": 0.2,
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=self.timeout)
        except requests.RequestException as exc:  # pragma: no cover - network failure guard
            logger.exception("Failed to contact OpenAI API")
            raise AgentAPIError("Unable to contact OpenAI API") from exc
        if response.status_code >= 400:
            try:
                detail = response.json()
            except ValueError:
                detail = response.text
            logger.error("OpenAI API error (%s): %s", response.status_code, detail)
            raise AgentAPIError(f"OpenAI API returned status {response.status_code}")

        try:
            payload = response.json()
            return payload["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError, ValueError) as exc:  # pragma: no cover - defensive
            logger.exception("Unexpected OpenAI response structure: %s", response.text)
            raise AgentAPIError("Unexpected response from OpenAI") from exc


__all__ = [
    "AgentAPIError",
    "AgentConfigurationError",
    "HealthSupportAgent",
]
