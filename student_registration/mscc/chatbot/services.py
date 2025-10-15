"""Integration with the ChatGPT API for the BMA assistant."""
from __future__ import annotations

import json
import time
from typing import Any, Dict, List, Optional

from django.conf import settings

try:  # pragma: no cover - defensive in case openai is missing in some envs
    from openai import OpenAI
except Exception:  # pragma: no cover
    OpenAI = None  # type: ignore

from .repository import BMAInsightsRepository
from .retriever import BMAInsightsRetriever


class BMAChatService:
    """Service responsible for orchestrating ChatGPT powered responses."""

    class ChatError(RuntimeError):

        """Raised when the chatbot cannot fulfil a request."""
        def __init__(self, message: str, *, status_code: Optional[int] = None):
            super().__init__(message)
            self.status_code = status_code

    retriever_class = BMAInsightsRetriever
    repository_class = BMAInsightsRepository

    def __init__(
        self,
        user,
        *,
        client=None,
        sleep=None,
        retriever_class=None,
        repository_class=None,
    ):
        self.user = user
        self._client = client
        self.model = getattr(settings, "OPENAI_BMA_MODEL", "gpt-4o-mini")
        self.max_tokens = getattr(settings, "OPENAI_BMA_MAX_TOKENS", 800)
        self.temperature = getattr(settings, "OPENAI_BMA_TEMPERATURE", 0.2)
        self.max_retries = max(getattr(settings, "OPENAI_BMA_MAX_RETRIES", 2), 0)
        self.retry_backoff = max(
            float(getattr(settings, "OPENAI_BMA_RETRY_BACKOFF", 1.0)), 0.0
        )
        self._sleep = sleep or time.sleep
        repository_cls = repository_class or self.repository_class
        self.repository = repository_cls(user)
        self._retriever_class = retriever_class or self.retriever_class

    # Public API ---------------------------------------------------------------
    def chat(
        self,
        *,
        question: str,
        history: Optional[List[Dict[str, str]]] = None,
    ) -> Dict[str, Any]:
        if not question or not question.strip():
            raise self.ChatError(
                "A question is required to query the chatbot.",
                status_code=400,
            )

        snapshot = self.repository.build_snapshot()
        context = self._build_context(snapshot, question)
        system_prompt = self._build_system_prompt(snapshot, context)
        messages = self._build_messages(system_prompt, history, question)

        client = self._client or self._build_client()
        last_error: Optional[BMAChatService.ChatError] = None
        response: Any = None
        for attempt in range(self.max_retries + 1):
            try:
                response = client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=self.temperature,
                    max_tokens=self.max_tokens,
                )
                break
            except Exception as exc:  # pragma: no cover - openai raises many subclasses
                error = self._map_openai_exception(exc)
                last_error = error
                if attempt < self.max_retries and self._should_retry(error):
                    self._sleep(self._retry_delay(exc, attempt))
                    continue
                raise error from exc
        else:  # pragma: no cover - safety net; loop always breaks or raises
            raise last_error or self.ChatError(
                "An unexpected error occurred while contacting the OpenAI service.",
                status_code=503,
            )

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

    def _build_context(self, snapshot: Dict[str, Any], question: str) -> str:
        if not self._retriever_class:
            return ""
        retriever = self._retriever_class(snapshot)
        return retriever.build_context(question, top_k=5)

    @staticmethod
    def _build_system_prompt(snapshot: Dict[str, Any], context: str) -> str:
        snapshot_json = json.dumps(snapshot, ensure_ascii=False)
        context_block = f"RELEVANT METRICS:\n{context}\n\n" if context else ""
        return (
            "You are the Beneficiary Monitoring & Assessment (BMA) analytics assistant. "
            "Use only the information contained in the provided JSON snapshot and the curated "
            "metrics to answer questions about registrations, schools, centres, partners, and "
            "trends. When data is unavailable, be transparent and explain any limitations. "
            "Respond with concise, well-structured Markdown.\n\n"
            f"{context_block}SNAPSHOT:\n{snapshot_json}"
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


    @staticmethod
    def _should_retry(error: "BMAChatService.ChatError") -> bool:
        if error.status_code in {429}:
            return True
        if error.status_code and error.status_code >= 500:
            return True
        return False

    def _retry_delay(self, exc: Exception, attempt: int) -> float:
        response = getattr(exc, "response", None)
        headers = getattr(response, "headers", None)
        retry_after = None
        if headers is not None and hasattr(headers, "get"):
            retry_after = headers.get("Retry-After") or headers.get("retry-after")
        if retry_after is not None:
            try:
                return float(retry_after)
            except (TypeError, ValueError):
                pass
        return self.retry_backoff * (2 ** attempt)

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
