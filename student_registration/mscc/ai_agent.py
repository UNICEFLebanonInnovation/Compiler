"""Utility helpers for the MSCC health support AI agent."""

from __future__ import annotations

import copy
import json
import logging
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Iterable, List, Sequence

import requests
from django.conf import settings

logger = logging.getLogger(__name__)


AGENT_STOP_WORDS = {
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


class AgentConfigurationError(RuntimeError):
    """Raised when the agent is not configured correctly."""


class AgentAPIError(RuntimeError):
    """Raised when the upstream OpenAI API returns an error."""


@dataclass(frozen=True)
class KnowledgeSearchResult:
    """Lightweight container returned by :class:`MSCCKnowledgeEngine`."""

    registration_id: int | None
    child_id: int | None
    score: float
    matched_terms: tuple[str, ...]
    snippet: str


class MSCCKnowledgeEngine:
    """Compile MSCC child context into a searchable knowledge base.

    The health agent already receives rich dictionaries describing each child.
    This helper flattens that structure into plain text "documents" that are
    easy to scan and tokenise.  The compiled representation keeps a small
    inverted index so staff (or automated routines) can quickly look up numbers
    and programme terms without wading through deeply nested JSON.
    """

    SECTION_SEPARATOR = "\n\n"

    def __init__(self, children_context: Iterable[dict] | None) -> None:
        self._children = [copy.deepcopy(child) for child in (children_context or []) if isinstance(child, dict)]
        self._documents: list[dict] = []
        self._vulnerability_profiles: list[dict] = []
        self._compiled_summary: str = ""
        self._enrich_children_with_vulnerabilities()
        self._build_documents()

    @staticmethod
    def _normalise_value(value) -> str:
        if value is None:
            return ""
        if isinstance(value, (datetime, date)):
            return value.isoformat()
        if isinstance(value, Decimal):
            return format(value, 'f')
        if isinstance(value, float):
            return f"{value:.4g}"
        return str(value)

    @staticmethod
    def _tokenise(text: str) -> set[str]:
        tokens = {
            token
            for token in re.findall(r"[a-zA-Z0-9']+", text.lower())
            if len(token) >= 2 and token not in AGENT_STOP_WORDS
        }
        return tokens

    @staticmethod
    def _extract_numbers(text: str) -> set[str]:
        return {match.group(0) for match in re.finditer(r"\d+(?:\.\d+)?", text)}

    def _build_documents(self) -> None:
        documents: list[dict] = []
        compiled_sections: list[str] = []

        for index, child in enumerate(self._children, start=1):
            lines: list[str] = []
            self._flatten(child, prefix=[], output=lines)
            document_text = "\n".join(lines)
            tokens = self._tokenise(document_text)
            numbers = self._extract_numbers(document_text)
            registration_id = child.get('registration_id')
            child_id = child.get('child_id')
            documents.append(
                {
                    'registration_id': registration_id,
                    'child_id': child_id,
                    'text': document_text,
                    'tokens': tokens,
                    'numbers': numbers,
                    'context': copy.deepcopy(child),
                    'vulnerability_profile': child.get('vulnerability_profile'),
                }
            )
            header = f"Child {index} – Registration {registration_id}"
            compiled_sections.append(f"{header}\n{document_text}")

        self._documents = documents
        self._compiled_summary = self.SECTION_SEPARATOR.join(compiled_sections).strip()

    def _enrich_children_with_vulnerabilities(self) -> None:
        profiles: list[dict] = []
        for child in self._children:
            profile = self._derive_vulnerability_profile(child)
            if profile:
                child['vulnerability_profile'] = profile
                child['vulnerability_tags'] = profile.get('top_concerns', [])[:5]
                profiles.append(profile)
            else:
                child['vulnerability_profile'] = {}
                child['vulnerability_tags'] = []
        self._vulnerability_profiles = profiles

    def _derive_vulnerability_profile(self, child: dict) -> dict:
        score = 0.0
        concerns: list[str] = []
        domain_scores: defaultdict[str, dict] = defaultdict(lambda: {'score': 0.0, 'concerns': []})

        def register_concern(message: str | None, *, domain: str | None = None, weight: float = 1.0, add_to_score: bool = True) -> None:
            nonlocal score
            if not message:
                return
            text = str(message).strip()
            if not text:
                return
            if text not in concerns:
                concerns.append(text)
            resolved_domain = domain or self._categorize_concern(text)
            bucket = domain_scores[resolved_domain]
            if text not in bucket['concerns']:
                bucket['concerns'].append(text)
            bucket['score'] += weight
            if add_to_score:
                score += weight

        risk_score = child.get('risk_score')
        if isinstance(risk_score, (int, float)):
            score += max(float(risk_score), 0.0)
            if risk_score >= 12:
                register_concern(
                    f'Composite risk score is {risk_score}',
                    domain='protection',
                    weight=2.5,
                    add_to_score=False,
                )

        life_quality = child.get('life_quality') or {}
        life_quality_score = life_quality.get('score')
        if isinstance(life_quality_score, (int, float)) and life_quality_score < 0:
            score += abs(float(life_quality_score))
            label = life_quality.get('label')
            if label:
                register_concern(
                    f'Life quality is {label.lower()}',
                    domain='wellbeing',
                    weight=2.0,
                    add_to_score=False,
                )
            for signal in life_quality.get('signals') or []:
                register_concern(signal.get('message'), weight=1.2)

        attendance = child.get('attendance') or {}
        missed = attendance.get('missed_sessions') or 0
        if isinstance(missed, (int, float)) and missed:
            if missed >= 3:
                register_concern(
                    f'{int(missed)} absences recorded recently',
                    domain='attendance',
                    weight=2.5,
                )
            elif missed >= 1:
                register_concern(
                    f'{int(missed)} absence recorded recently',
                    domain='attendance',
                    weight=1.5,
                )
        rate = attendance.get('attendance_rate')
        if isinstance(rate, (int, float)) and rate < 0.85:
            percentage = round(rate * 100)
            if percentage < 75:
                weight = 2.5
            elif percentage < 85:
                weight = 1.5
            else:
                weight = 1.0
            register_concern(
                f'Attendance rate at {percentage}% (below programme threshold)',
                domain='attendance',
                weight=weight,
            )

        services = child.get('services') or {}
        service_domain_labels = {
            'pss': 'psychosocial',
            'health': 'health',
            'support': 'support',
            'education': 'education',
        }
        for key, summary in services.items():
            if not isinstance(summary, dict):
                continue
            pending = summary.get('required_pending') or 0
            if not pending:
                continue
            domain = service_domain_labels.get(key, self._categorize_concern(key))
            weight = 3.0 if key == 'pss' else 2.0 if key == 'health' else 1.5
            message = f"{key.upper()} pending required services ({pending})"
            register_concern(message, domain=domain, weight=weight * float(pending))

        wellbeing_flags = child.get('wellbeing_flags') or []
        for flag in wellbeing_flags:
            register_concern(flag, weight=1.8)

        alerts = child.get('alerts') or []
        for alert in alerts:
            register_concern(alert, weight=1.5)

        family_context = child.get('family_context') or {}
        for flag in family_context.get('flags') or []:
            register_concern(flag, domain='family', weight=1.2)

        programme_impact = child.get('programme_impact') or {}
        direction = (programme_impact.get('direction') or '').lower()
        if direction in {'negative', 'mixed'}:
            weight = 2.5 if direction == 'negative' else 1.5
            register_concern(
                f'Programme impact trend is {direction}',
                domain='education',
                weight=weight,
            )

        if not concerns and score <= 0:
            return {}

        severity = self._severity_from_score(score)
        domain_breakdown = [
            {
                'domain': domain,
                'score': round(info['score'], 2),
                'concerns': info['concerns'],
            }
            for domain, info in domain_scores.items()
        ]
        domain_breakdown.sort(key=lambda entry: entry['score'], reverse=True)

        top_concerns = concerns[:6]

        if top_concerns:
            summary = f"{severity.title()} vulnerability driven by {top_concerns[0]}."
            if len(top_concerns) >= 2:
                summary += f" Additional concern: {top_concerns[1]}."
            if len(top_concerns) > 2:
                summary += " Further flagged areas: " + ", ".join(top_concerns[2:4]) + "."
        else:
            summary = 'No significant vulnerabilities detected.'

        return {
            'score': round(score, 2),
            'severity': severity,
            'primary_domain': domain_breakdown[0]['domain'] if domain_breakdown else None,
            'top_concerns': top_concerns,
            'concern_count': len(concerns),
            'domain_breakdown': domain_breakdown,
            'summary': summary,
        }

    @staticmethod
    def _severity_from_score(score: float) -> str:
        if score >= 22:
            return 'critical'
        if score >= 14:
            return 'high'
        if score >= 7:
            return 'moderate'
        if score >= 3:
            return 'elevated'
        return 'low'

    @staticmethod
    def _categorize_concern(message: str) -> str:
        if not isinstance(message, str):
            return 'general'
        text = message.lower()
        if any(keyword in text for keyword in {'attendance', 'absenc', 'presence'}):
            return 'attendance'
        if any(keyword in text for keyword in {'nutrition', 'muac', 'malnutrition', 'feeding'}):
            return 'nutrition'
        if any(keyword in text for keyword in {'health', 'clinic', 'medical', 'referral'}):
            return 'health'
        if any(keyword in text for keyword in {'pss', 'psychosocial', 'distress', 'wellbeing'}):
            return 'psychosocial'
        if any(keyword in text for keyword in {'education', 'learning', 'school'}):
            return 'education'
        if any(keyword in text for keyword in {'family', 'caregiver', 'parent'}):
            return 'family'
        if any(keyword in text for keyword in {'labour', 'protection', 'safety'}):
            return 'protection'
        if any(keyword in text for keyword in {'support', 'cash', 'assistance'}):
            return 'support'
        return 'general'

    def _flatten(self, value, *, prefix: list[str], output: list[str]) -> None:
        if isinstance(value, dict):
            for key in sorted(value):
                self._flatten(value[key], prefix=prefix + [str(key)], output=output)
            return
        if isinstance(value, (list, tuple)):
            for position, item in enumerate(value):
                self._flatten(item, prefix=prefix + [str(position)], output=output)
            return

        field_path = ".".join(prefix)
        normalised = self._normalise_value(value)
        if normalised:
            output.append(f"{field_path} = {normalised}")

    @property
    def documents(self) -> list[dict]:
        """Return the indexed documents."""

        return list(self._documents)

    @property
    def enriched_children(self) -> list[dict]:
        """Return enriched child contexts including vulnerability profiles."""

        return [copy.deepcopy(child) for child in self._children]

    @property
    def vulnerability_profiles(self) -> list[dict]:
        """Return vulnerability profiles computed during compilation."""

        return [copy.deepcopy(profile) for profile in self._vulnerability_profiles]

    @property
    def vulnerability_overview(self) -> dict:
        """Aggregate vulnerability signals across all children."""

        if not self._children:
            return {}

        severity_counts: Counter[str] = Counter()
        domain_counts: Counter[str] = Counter()
        concern_counts: Counter[str] = Counter()

        for child in self._children:
            profile = child.get('vulnerability_profile') or {}
            severity = profile.get('severity') or 'unknown'
            severity_counts[severity] += 1
            for entry in profile.get('domain_breakdown') or []:
                domain = entry.get('domain')
                if domain:
                    domain_counts[domain] += 1
            for concern in profile.get('top_concerns') or []:
                concern_counts[concern] += 1

        overview: dict = {'total_children': len(self._children)}
        if severity_counts:
            overview['severity_counts'] = dict(
                sorted(severity_counts.items(), key=lambda item: (-item[1], item[0]))
            )
        if domain_counts:
            overview['domain_counts'] = dict(
                sorted(domain_counts.items(), key=lambda item: (-item[1], item[0]))
            )
        if concern_counts:
            overview['top_concerns'] = [
                {'concern': concern, 'count': count}
                for concern, count in concern_counts.most_common(10)
            ]
        return overview

    def render_compiled_summary(self) -> str:
        """Return a readable text dump of all indexed children."""

        return self._compiled_summary

    def search(self, query: str, *, limit: int = 5) -> list[KnowledgeSearchResult]:
        """Search the compiled knowledge using keyword and numeric matches."""

        if not isinstance(query, str):
            return []

        query_tokens = self._tokenise(query)
        query_numbers = self._extract_numbers(query)
        if not query_tokens and not query_numbers:
            return []

        ranked: list[tuple[float, dict, set[str]]] = []
        for document in self._documents:
            token_matches = query_tokens & document['tokens'] if query_tokens else set()
            number_matches = query_numbers & document['numbers'] if query_numbers else set()
            if not token_matches and not number_matches:
                continue
            score = float(len(token_matches)) + 1.5 * float(len(number_matches))
            ranked.append((score, document, token_matches | number_matches))

        ranked.sort(key=lambda item: item[0], reverse=True)
        results: list[KnowledgeSearchResult] = []
        for score, document, matches in ranked[:limit]:
            snippet = self._build_snippet(document['text'], matches)
            results.append(
                KnowledgeSearchResult(
                    registration_id=document.get('registration_id'),
                    child_id=document.get('child_id'),
                    score=round(score, 2),
                    matched_terms=tuple(sorted(matches)),
                    snippet=snippet,
                )
            )

        return results

    @staticmethod
    def _build_snippet(document_text: str, matches: set[str]) -> str:
        if not document_text:
            return ""
        if not matches:
            return document_text.splitlines()[0]

        lines = document_text.splitlines()
        for line in lines:
            for term in matches:
                if term.lower() in line.lower():
                    return line
        return lines[0]


class HealthSupportAgent:
    """Simple wrapper around the OpenAI chat completion endpoint."""

    STOP_WORDS = AGENT_STOP_WORDS

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
        'caregiver': {'support', 'family'},
        'family': {'family'},
        'parent': {'family'},
        'household': {'family'},
        'follow': {'family'},
        'followup': {'family'},
        'follow-up': {'family'},
        'socioeconomic': {'family'},
        'livelihood': {'family'},
        'poverty': {'family'},
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
        knowledge_engine = MSCCKnowledgeEngine(children_context)
        summary = knowledge_engine.render_compiled_summary() or json.dumps(
            children_context, indent=2, default=str
        )
        system_message = (
            "You are an expert public health analyst supporting the MSCC "
            "(Makani Strategic Child Care) programme."
        )
        user_instructions = (
            "Review the children information and highlight who requires urgent "
            "support or follow-up. Consider age, psychosocial (PSS) services, "
            "health services, attendance history, and other support needs. "
            "Incorporate family follow-up actions, socio-economic stability, "
            "and caregiver engagement in education when prioritising cases. "
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
            if 'family' in focus_topics:
                scope_instruction += (
                    " Highlight family follow-up efforts, caregiver "
                    "participation, socio-economic pressures, and how the "
                    "household context affects wellbeing and learning."
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
    "KnowledgeSearchResult",
    "MSCCKnowledgeEngine",
    "HealthSupportAgent",
    "PreAssessmentAgent",
]
