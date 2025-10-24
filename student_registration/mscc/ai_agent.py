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


class PreAssessmentAgent:
    """Lightweight analyser that validates staff questions before querying."""

    PROFANITY = {
        'shit',
        'shitty',
        'fuck',
        'fucking',
        'damn',
        'crap',
    }

    KEYBOARD_ROWS = (
        'qwertyuiop',
        'asdfghjkl',
        'zxcvbnm',
    )

    def __init__(self, min_tokens: int = 2) -> None:
        self.min_tokens = min_tokens

    def evaluate(self, question: str | None) -> dict:
        """Return an assessment describing whether a question is actionable."""

        normalized = question.strip() if isinstance(question, str) else ""
        result = {
            'question': normalized,
            'is_empty': not normalized,
            'is_meaningful': False,
            'quality_score': 0.0,
            'confidence': 'low',
            'keywords': [],
            'focus_topics': [],
            'issues': [],
            'should_abort': False,
            'summary': '',
            'profanity_detected': False,
            'token_count': 0,
            'recommended_action': '',
        }

        if not normalized:
            result['summary'] = (
                'No focus question provided; the assistant will prioritise the most '
                'critical risks detected in the data.'
            )
            result['recommended_action'] = (
                'Consider adding a focus question to tailor the prioritisation for your needs.'
            )
            result['issues'] = ['No question provided; default prioritisation will be used.']
            return result

        tokens = re.findall(r"[a-zA-Z']+", normalized.lower())
        filtered_tokens = [token for token in tokens if len(token) >= 3]
        unique_tokens = set(filtered_tokens)
        vowel_tokens = [token for token in filtered_tokens if re.search('[aeiou]', token)]
        vowel_ratio = (len(vowel_tokens) / len(filtered_tokens)) if filtered_tokens else 0.0
        profanity_tokens = [token for token in filtered_tokens if token in self.PROFANITY]

        keywords = HealthSupportAgent.extract_keywords(normalized)
        focus_topics = sorted(HealthSupportAgent.infer_focus_topics(normalized))
        recognized_keyword_count = sum(
            1 for keyword in keywords if keyword in HealthSupportAgent.KEYWORD_TOPIC_MAP
        )

        quality = 0.0
        quality += 0.25  # baseline for providing any input
        if len(normalized) >= 40:
            quality += 0.15
        if len(filtered_tokens) >= self.min_tokens:
            quality += 0.2
        if len(unique_tokens) >= max(self.min_tokens, 3):
            quality += 0.1
        if recognized_keyword_count:
            quality += 0.2
        elif keywords:
            quality += 0.05
        if focus_topics:
            quality += 0.2
        if len(normalized) >= 120:
            quality += 0.1

        gibberish_detected = bool(filtered_tokens) and vowel_ratio < 0.3
        if gibberish_detected:
            quality -= 0.4
            result['issues'].append('The wording looks unclear or non-sensical.')

        keyboard_walk_tokens = [
            token
            for token in filtered_tokens
            if any(token in row or token[::-1] in row for row in self.KEYBOARD_ROWS)
        ]
        if filtered_tokens:
            keyboard_walk_ratio = len(keyboard_walk_tokens) / len(filtered_tokens)
        else:
            keyboard_walk_ratio = 0.0
        if keyboard_walk_ratio >= 0.5:
            quality -= 0.35
            result['issues'].append('The wording appears to be keyboard gibberish; please clarify the request.')

        if profanity_tokens:
            quality -= 0.3
            result['issues'].append('The question contains flagged language.')
            result['profanity_detected'] = True

        if len(filtered_tokens) < self.min_tokens:
            result['issues'].append('The question is too short to understand the intent.')

        if not focus_topics:
            result['issues'].append(
                'No programme focus detected; results may be generic unless the question is refined.'
            )
        if keywords and not recognized_keyword_count:
            result['issues'].append('No recognised programme keywords were detected.')

        quality = max(0.0, min(1.0, quality))
        is_meaningful = quality >= 0.5 or bool(focus_topics)
        should_abort = bool(normalized) and (
            (quality < 0.35 and not focus_topics)
            or (
                not focus_topics
                and not recognized_keyword_count
                and keyboard_walk_ratio >= 0.5
            )
        )

        result.update(
            {
                'is_meaningful': is_meaningful,
                'quality_score': round(quality, 2),
                'confidence': 'high' if quality >= 0.75 else 'medium' if quality >= 0.5 else 'low',
                'keywords': keywords,
                'focus_topics': focus_topics,
                'should_abort': should_abort,
                'token_count': len(filtered_tokens),
            }
        )

        if should_abort:
            result['summary'] = (
                'The question could not be matched to Makani programme themes. '
                'Please rephrase it with specific outcomes or services to analyse.'
            )
            result['recommended_action'] = (
                'Rephrase the question with programme keywords (e.g., nutrition, attendance, PSS) '
                'or specify the outcomes you want to review.'
            )
        elif not is_meaningful:
            result['summary'] = (
                'The question may be ambiguous; the assistant will still run a generic triage.'
            )
            result['recommended_action'] = (
                'Add specific programme areas or child outcomes to sharpen the assessment focus.'
            )
        else:
            result['summary'] = 'Question understood; tailoring the assessment accordingly.'
            result['recommended_action'] = (
                'Proceeding with the tailored analysis based on the detected focus areas.'
            )

        if focus_topics:
            result['summary'] += f" Focus areas detected: {', '.join(focus_topics)}."

        if not result['issues']:
            result['issues'] = ['No issues detected.']

        return result


__all__ = [
    "AgentAPIError",
    "AgentConfigurationError",
    "HealthSupportAgent",
    "PreAssessmentAgent",
]
