"""Utility helpers for the MSCC health support AI agent."""

from __future__ import annotations

import json
import logging
import re
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

    STOP_WORDS = {
        'the',
        'and',
        'for',
        'with',
        'that',
        'this',
        'from',
        'into',
        'about',
        'need',
        'please',
        'could',
        'would',
        'should',
        'like',
        'make',
        'have',
        'has',
        'had',
        'are',
        'was',
        'were',
        'can',
        'help',
        'assist',
        'focus',
        'around',
        'into',
        'insight',
        'insights',
        'information',
        'status',
        'provide',
        'providing',
        'look',
        'looking',
        'tell',
        'show',
        'question',
        'questions',
        'kids',
        'child',
        'children',
        'programme',
        'program',
        'mscc',
        'over',
        'year',
        'years',
        'round',
        'rounds',
    }

    KEYWORD_TOPIC_MAP = {
        'nutrition': {'nutrition'},
        'malnutrition': {'nutrition'},
        'feeding': {'nutrition'},
        'diet': {'nutrition'},
        'food': {'nutrition'},
        'health': {'health'},
        'medical': {'health'},
        'clinic': {'health'},
        'attendance': {'attendance'},
        'absent': {'attendance'},
        'presence': {'attendance'},
        'pss': {'pss'},
        'psycho': {'pss'},
        'psychosocial': {'pss'},
        'support': {'support'},
        'caregiver': {'support'},
        'case': {'support'},
        'education': {'education'},
        'school': {'education'},
        'learning': {'education'},
        'grade': {'education'},
        'improvement': {'education', 'impact'},
        'decline': {'education', 'impact'},
        'impact': {'impact'},
        'progress': {'education', 'impact'},
        'risk': {'impact'},
        'risks': {'impact'},
        'wellbeing': {'wellbeing'},
        'quality': {'wellbeing'},
        'sentiment': {'wellbeing'},
        'life': {'wellbeing'},
        'history': {'registration'},
        'registration': {'registration'},
        'profile': {'registration'},
    }

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
        keywords: Sequence[str] | None = None,
    ) -> str:
        """Generate an analysis for the supplied children context."""

        if focus_topics is None:
            focus_topics = self.infer_focus_topics(question)

        if keywords is None:
            keywords = self.extract_keywords(question)

        messages = self._build_prompt(
            children_context,
            question=question,
            focus_topics=focus_topics,
            keywords=keywords,
        )
        return self._request_chat_completion(messages)

    def _build_prompt(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
        keywords: Sequence[str] | None = None,
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
            "Provide actionable recommendations for each child. Evaluate the "
            "Makani programme impact over the years and clarify whether it "
            "appears positive, negative, or mixed for each case."
        )
        formatting = (
            "Return your response in markdown with the sections 'Priority Cases', "
            "'Watch List', and 'Key Programme Insights'. List each child with "
            "their registration id and a short rationale."
        )

        focus_topics = set(focus_topics or [])
        question_text = (question or "").strip()
        keywords = [keyword for keyword in (keywords or []) if keyword]
        if question_text:
            user_instructions = (
                f"{user_instructions}\n\nFocus specifically on: {question_text}"
            )
        else:
            user_instructions = (
                f"{user_instructions}\n\nIf no focus question is provided, explain "
                "that the assessment defaults to the most critical risk "
                "factors detected in the data."
            )

        if keywords:
            detected = ", ".join(keywords)
            user_instructions = (
                f"{user_instructions}\n\nDetected question keywords: {detected}. "
                "Explicitly address these themes in your findings and "
                "rationale."
            )
        elif question_text:
            user_instructions = (
                f"{user_instructions}\n\nThe staff question lacks clear programme "
                "keywords. Provide a concise general triage and note that "
                "the query was ambiguous."
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

    @classmethod
    def infer_focus_topics(cls, question: str | None) -> set[str]:
        """Derive focus topics from the staff question for prompt tailoring."""

        if not isinstance(question, str):
            return set()

        text = question.lower()
        keywords = cls.extract_keywords(question)
        focus = set()
        for keyword, topics in cls.KEYWORD_TOPIC_MAP.items():
            if keyword in text or keyword in keywords:
                focus.update(topics)

        return focus

    @staticmethod
    def extract_keywords(question: str | None, limit: int = 5) -> list[str]:
        """Return the most relevant keywords derived from a question."""

        if not isinstance(question, str):
            return []

        tokens = re.findall(r"[a-zA-Z']+", question.lower())
        keywords: list[str] = []
        for token in tokens:
            if len(token) < 3:
                continue
            if token in HealthSupportAgent.STOP_WORDS:
                continue
            if token not in keywords:
                keywords.append(token)
            if len(keywords) >= limit:
                break

        return keywords

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
        except requests.exceptions.Timeout as exc:  # pragma: no cover - explicit timeout guard
            logger.exception(
                "OpenAI API request timed out after %s seconds", self.timeout
            )
            raise AgentAPIError(
                "OpenAI API request timed out. Please try again in a moment."
            ) from exc
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
