"""Integration with the ChatGPT API for the BMA assistant."""
from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from django.conf import settings

try:  # pragma: no cover - defensive in case openai is missing in some envs
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

from .repository import BMAInsightsRepository


class BMAChatService:
    """Service responsible for orchestrating ChatGPT powered responses."""

    class ChatError(RuntimeError):
        """Raised when the chatbot cannot fulfil a request."""

    def __init__(self, user, *, client=None):
        self.user = user
        self._client = client
        self.model = getattr(settings, "OPENAI_BMA_MODEL", "gpt-4o-mini")
        self.max_tokens = getattr(settings, "OPENAI_BMA_MAX_TOKENS", 800)
        self.temperature = getattr(settings, "OPENAI_BMA_TEMPERATURE", 0.2)
        self.repository = BMAInsightsRepository(user)

    # Public API ---------------------------------------------------------------
    def chat(
        self,
        *,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if not question or not question.strip():
            raise self.ChatError("A question is required to query the chatbot.")

        snapshot = self.repository.build_snapshot()
        system_prompt = self._build_system_prompt(snapshot)
        messages = self._build_messages(system_prompt, history, question)

        client = self._client or self._build_client()
        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
            )
        except Exception as exc:  # pragma: no cover - openai raises many subclasses
            raise self.ChatError(f"ChatGPT API error: {exc}") from exc

        answer = self._extract_answer(response)
        usage = self._extract_usage(response)
        return {
            "answer": answer,
            "snapshot": snapshot,
            "usage": usage,
        }

    # Helpers -----------------------------------------------------------------
    def _build_client(self):
        if self._client:
            return self._client
        if OpenAI is None:
            raise self.ChatError("The OpenAI client library is not available.")
        api_key = getattr(settings, "OPENAI_API_KEY", None)
        if not api_key:
            raise self.ChatError("OpenAI API key is not configured.")
        return OpenAI(api_key=api_key)

    @staticmethod
    def _build_system_prompt(snapshot: Dict[str, Any]) -> str:
        snapshot_json = json.dumps(snapshot, ensure_ascii=False)
        return (
            "You are the Beneficiary Monitoring & Assessment (BMA) analytics assistant. "
            "Use only the information contained in the provided JSON snapshot to answer "
            "questions about registrations, schools, centres, partners, and trends. "
            "When data is unavailable, be transparent and explain any limitations. "
            "Respond with concise, well-structured Markdown.\n\n"
            f"SNAPSHOT:\n{snapshot_json}"
        )

    @staticmethod
    def _build_messages(
        system_prompt: str,
        history: Optional[List[Dict[str, str]]],
        question: str,
    ) -> List[Dict[str, str]]:
        messages: List[Dict[str, str]] = [{"role": "system", "content": system_prompt}]
        for message in history or []:
            role = message.get("role")
            content = (message.get("content") or "").strip()
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})
        messages.append({"role": "user", "content": question.strip()})
        return messages

    @classmethod
    def _extract_answer(cls, response: Any) -> str:
        try:
            choice = response.choices[0]
            message = getattr(choice, "message", None)
            if isinstance(message, dict):
                content = message.get("content")
            else:
                content = getattr(message, "content", None)
        except Exception as exc:  # pragma: no cover - defensive
            raise cls.ChatError("Unexpected response format from ChatGPT.") from exc

        if isinstance(content, list):  # Newer API can return parts
            content = "".join(part.get("text", "") for part in content if isinstance(part, dict))
        if not isinstance(content, str):
            raise cls.ChatError("ChatGPT response did not contain text.")
        return content.strip()

    @staticmethod
    def _extract_usage(response: Any) -> Optional[Dict[str, int]]:
        usage = getattr(response, "usage", None)
        if usage is None:
            return None
        keys = ("prompt_tokens", "completion_tokens", "total_tokens")
        if isinstance(usage, dict):
            return {key: usage.get(key) for key in keys if key in usage}
        return {key: getattr(usage, key, None) for key in keys if hasattr(usage, key)}
