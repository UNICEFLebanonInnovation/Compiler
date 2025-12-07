"""Utility helpers for the MSCC AI agents."""

from __future__ import annotations

import copy
import json
import logging
import re
import time
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
        education_overview = self._aggregate_education_outcomes()
        if education_overview:
            overview['education_improvement'] = education_overview
        center_risk_assessment = self.detect_high_risk_centers()
        overview['center_risk_assessment'] = center_risk_assessment
        flagged_centers = [
            entry
            for entry in center_risk_assessment
            if entry['is_high_vulnerability_center'] or entry['is_high_child_protection_center']
        ]
        if flagged_centers:
            overview['flagged_centers'] = flagged_centers
        return overview

    @staticmethod
    def _extract_center_name(registration_details: list | None) -> str | None:
        if not isinstance(registration_details, list):
            return None
        for entry in registration_details:
            if not isinstance(entry, dict):
                continue
            if entry.get('field') == 'center':
                value = entry.get('value')
                if value:
                    return str(value)
        return None

    def detect_high_risk_centers(
        self,
        *,
        vulnerability_ratio_threshold: float = 0.35,
        vulnerability_count_threshold: int = 3,
        protection_ratio_threshold: float = 0.25,
        protection_count_threshold: int = 2,
        high_score_threshold: float = 14.0,
    ) -> list[dict]:
        """Return centre-level risk assessments derived from child wellbeing data."""

        centers: dict[tuple[int | None, str | None], dict] = {}
        for child in self._children:
            center_id = child.get('center_id')
            center_name = child.get('center_name')
            if not center_name:
                center_name = self._extract_center_name(child.get('registration_details'))
            if center_id is None and not center_name:
                continue
            key = (center_id, center_name)
            entry = centers.setdefault(
                key,
                {
                    'center_id': center_id,
                    'center_name': center_name,
                    'total_children': 0,
                    'high_vulnerability_children': 0,
                    'child_protection_cases': 0,
                    'scores': [],
                },
            )

            entry['total_children'] += 1

            profile = child.get('vulnerability_profile') or {}
            severity = str(profile.get('severity') or '').lower()
            score = profile.get('score')
            if isinstance(score, (int, float)):
                entry['scores'].append(float(score))
            if severity in {'high', 'critical'} or (
                isinstance(score, (int, float)) and float(score) >= high_score_threshold
            ):
                entry['high_vulnerability_children'] += 1

            has_protection_flag = False
            for flag in child.get('wellbeing_flags') or []:
                if isinstance(flag, str) and 'protection' in flag.lower():
                    has_protection_flag = True
                    break
            if not has_protection_flag:
                for breakdown in profile.get('domain_breakdown') or []:
                    domain = str(breakdown.get('domain') or '').lower()
                    if domain != 'protection':
                        continue
                    score_value = breakdown.get('score')
                    if isinstance(score_value, (int, float)) and score_value > 0:
                        has_protection_flag = True
                        break
            if has_protection_flag:
                entry['child_protection_cases'] += 1

        assessments: list[dict] = []
        for (center_id, center_name), data in centers.items():
            total = data['total_children']
            vulnerability_ratio = data['high_vulnerability_children'] / total if total else 0.0
            protection_ratio = data['child_protection_cases'] / total if total else 0.0
            scores = [score for score in data['scores'] if score is not None]
            average_score = sum(scores) / len(scores) if scores else None

            high_vulnerability_flag = (
                data['high_vulnerability_children'] >= vulnerability_count_threshold
                or vulnerability_ratio >= vulnerability_ratio_threshold
                or (average_score is not None and average_score >= high_score_threshold)
            )
            high_protection_flag = (
                data['child_protection_cases'] >= protection_count_threshold
                or protection_ratio >= protection_ratio_threshold
            )

            reasons: list[str] = []
            if high_vulnerability_flag:
                if vulnerability_ratio >= vulnerability_ratio_threshold and total:
                    reasons.append(
                        f"{round(vulnerability_ratio * 100)}% of assessed children show high vulnerabilities."
                    )
                if data['high_vulnerability_children'] >= vulnerability_count_threshold:
                    reasons.append(
                        f"{data['high_vulnerability_children']} children flagged with high vulnerabilities."
                    )
                if average_score is not None and average_score >= high_score_threshold:
                    reasons.append(
                        f"Average vulnerability score {average_score:.1f} exceeds threshold {high_score_threshold:.0f}."
                    )
            if high_protection_flag:
                if protection_ratio >= protection_ratio_threshold and total:
                    reasons.append(
                        f"{round(protection_ratio * 100)}% of children have child protection concerns."
                    )
                if data['child_protection_cases'] >= protection_count_threshold:
                    reasons.append(
                        f"{data['child_protection_cases']} child protection cases reported."
                    )

            display_name = center_name or 'Unknown center'

            assessments.append(
                {
                    'center_id': center_id,
                    'center_name': display_name,
                    'center_label': center_name,
                    'total_children': total,
                    'high_vulnerability_children': data['high_vulnerability_children'],
                    'high_vulnerability_ratio': round(vulnerability_ratio, 2) if total else 0.0,
                    'average_vulnerability_score': round(average_score, 2)
                    if average_score is not None
                    else None,
                    'child_protection_cases': data['child_protection_cases'],
                    'child_protection_ratio': round(protection_ratio, 2) if total else 0.0,
                    'is_high_vulnerability_center': high_vulnerability_flag,
                    'is_high_child_protection_center': high_protection_flag,
                    'reasons': reasons,
                }
            )

        assessments.sort(
            key=lambda item: (
                1 if (item['is_high_vulnerability_center'] or item['is_high_child_protection_center']) else 0,
                item['high_vulnerability_ratio'],
                item['child_protection_ratio'],
            ),
            reverse=True,
        )
        return assessments

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

    def _aggregate_education_outcomes(self) -> dict | None:
        """Aggregate education pre/post-test outcomes across all children."""

        subject_stats: dict[str, dict] = {}
        average_changes: list[float] = []
        children_with_assessment = 0
        post_test_completed = 0

        def _coerce_number(value):
            if isinstance(value, Decimal):
                return float(value)
            if isinstance(value, (int, float)):
                return float(value)
            return None

        for child in self._children:
            progress = child.get('education_progress') or {}
            if not isinstance(progress, dict) or not progress:
                continue

            children_with_assessment += 1
            avg_change = _coerce_number(progress.get('average_change'))
            if avg_change is not None:
                average_changes.append(avg_change)

            post_test_flag = str(progress.get('post_test_done') or '').strip().lower()
            if post_test_flag == 'yes':
                post_test_completed += 1

            for subject in progress.get('subjects') or []:
                if not isinstance(subject, dict):
                    continue

                field = subject.get('field')
                label = subject.get('label') or (field.replace('_', ' ').title() if isinstance(field, str) else None)
                key = field or label
                if not key:
                    continue

                entry = subject_stats.setdefault(
                    key,
                    {
                        'field': field,
                        'label': label,
                        'pre_scores': [],
                        'post_scores': [],
                        'changes': [],
                        'improved_children': 0,
                        'declined_children': 0,
                        'stable_children': 0,
                        'observations': 0,
                    },
                )

                observed = False
                pre_score = _coerce_number(subject.get('pre'))
                if pre_score is not None:
                    entry['pre_scores'].append(pre_score)
                    observed = True

                post_score = _coerce_number(subject.get('post'))
                if post_score is not None:
                    entry['post_scores'].append(post_score)
                    observed = True

                change_value = _coerce_number(subject.get('change'))
                if change_value is not None:
                    entry['changes'].append(change_value)
                    if change_value > 0:
                        entry['improved_children'] += 1
                    elif change_value < 0:
                        entry['declined_children'] += 1
                    else:
                        entry['stable_children'] += 1
                    observed = True

                if observed:
                    entry['observations'] += 1

        if not subject_stats and not average_changes and not children_with_assessment:
            return None

        def _classify_trend(value: float | None) -> str | None:
            if value is None:
                return None
            if value >= 5:
                return 'improved'
            if value <= -5:
                return 'declined'
            return 'stable'

        subjects_overview: list[dict] = []
        improving_subjects: list[str] = []
        declining_subjects: list[str] = []

        for key, stats in sorted(subject_stats.items(), key=lambda item: (item[1]['label'] or item[0] or '')):
            avg_change = None
            if stats['changes']:
                avg_change = round(sum(stats['changes']) / len(stats['changes']), 2)
            avg_pre = None
            if stats['pre_scores']:
                avg_pre = round(sum(stats['pre_scores']) / len(stats['pre_scores']), 2)
            avg_post = None
            if stats['post_scores']:
                avg_post = round(sum(stats['post_scores']) / len(stats['post_scores']), 2)

            trend = _classify_trend(avg_change)
            if trend == 'improved' and stats['label']:
                improving_subjects.append(stats['label'])
            if trend == 'declined' and stats['label']:
                declining_subjects.append(stats['label'])

            change_observations = len(stats['changes'])
            improvement_rate = None
            if change_observations:
                improvement_rate = round(stats['improved_children'] / change_observations, 2)

            subjects_overview.append(
                {
                    'field': stats['field'],
                    'label': stats['label'],
                    'average_pre': avg_pre,
                    'average_post': avg_post,
                    'average_change': avg_change,
                    'direction': trend,
                    'observations': stats['observations'],
                    'change_observations': change_observations,
                    'improved_children': stats['improved_children'],
                    'declined_children': stats['declined_children'],
                    'stable_children': stats['stable_children'],
                    'improvement_rate': improvement_rate,
                }
            )

        overall_change = None
        if average_changes:
            overall_change = round(sum(average_changes) / len(average_changes), 2)
        overall_direction = _classify_trend(overall_change)

        completion_rate = None
        if children_with_assessment:
            completion_rate = round(post_test_completed / children_with_assessment, 2)

        return {
            'children_with_assessments': children_with_assessment,
            'average_change': overall_change,
            'overall_direction': overall_direction,
            'post_test_completion_rate': completion_rate,
            'subjects': subjects_overview,
            'subjects_improving': improving_subjects,
            'subjects_declining': declining_subjects,
        }


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
        max_retries: int | None = None,
        retry_backoff: float | None = None,
    ) -> None:
        self.api_key = api_key or getattr(settings, "OPENAI_API_KEY", "")
        if not self.api_key:
            raise AgentConfigurationError("OpenAI API key is not configured.")

        self.model = model or getattr(settings, "OPENAI_HEALTH_AGENT_MODEL", "gpt-4o-mini")
        self.base_url = base_url or getattr(settings, "OPENAI_API_BASE", "https://api.openai.com/v1")
        self.timeout = timeout or int(getattr(settings, "OPENAI_TIMEOUT", 30))
        retries_setting = int(getattr(settings, "OPENAI_MAX_RETRIES", 3))
        retries = max_retries if max_retries is not None else retries_setting
        self.max_retries = max(1, int(retries))
        backoff_setting = float(getattr(settings, "OPENAI_RETRY_BACKOFF", 1.0))
        backoff = retry_backoff if retry_backoff is not None else backoff_setting
        self.retry_backoff = max(0.0, float(backoff))

    def _retry_delay(self, attempt: int) -> float:
        return self.retry_backoff * (2 ** (attempt - 1))

    def analyze_children(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
        keywords: Sequence[str] | None = None,
        programme_overview: dict | None = None,
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
            programme_overview=programme_overview,
        )
        return self._request_chat_completion(messages)

    def _build_prompt(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
        keywords: Sequence[str] | None = None,
        programme_overview: dict | None = None,
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
            "Detect early signs of vulnerability among the registered children, "
            "calling out emerging risk factors or deteriorating trends that may "
            "need proactive attention. Provide actionable recommendations for "
            "each child. Recommendations must respond strictly to the staff "
            "question or stated focus domains—omit unrelated advice and state "
            "when information is insufficient. Evaluate the Makani programme "
            "impact over the years and clarify whether it appears positive, "
            "negative, or mixed for each case. Quantify how well each centre "
            "supports children's wellbeing by reporting proportions or counts "
            "of children who regularly attend, complete core services, or need "
            "further follow-up, and flag data gaps when calculations are not "
            "possible. Summarise education improvement for each learning "
            "material using available pre-test and post-test results, noting "
            "notable gains or declines."
        )
        formatting = (
            "Return your response in markdown with the sections 'Priority Cases', "
            "'Watch List', and 'Key Programme Insights'. List each child with "
            "their registration id and a short rationale. In 'Key Programme "
            "Insights', include the centre-level wellbeing metrics you "
            "calculated, highlighting attendance, service completion, and "
            "follow-up needs. Use the aggregated programme overview data "
            "provided (covering all eligible children before any review limit) "
            "when reporting centre-wide metrics so counts are not capped by the "
            "Maximum children to review setting."
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

        overview_appendix = ""
        if programme_overview:
            try:
                overview_text = json.dumps(programme_overview, indent=2, default=str)
            except TypeError:
                overview_text = str(programme_overview)
            overview_appendix = (
                "\n\nAggregated programme overview (all eligible children before applying review limits):\n"
                f"{overview_text}"
            )

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    f"{user_instructions}\n\n{formatting}\n\nChildren data:\n{summary}{overview_appendix}"
                ),
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

        response = None
        for attempt in range(1, self.max_retries + 1):
            try:
                response = requests.post(
                    url, headers=headers, json=payload, timeout=self.timeout
                )
            except requests.exceptions.Timeout as exc:  # pragma: no cover - explicit timeout guard
                if attempt == self.max_retries:
                    logger.exception(
                        "OpenAI API request timed out after %s seconds", self.timeout
                    )
                    raise AgentAPIError(
                        "OpenAI API request timed out. Please try again in a moment."
                    ) from exc

                delay = self._retry_delay(attempt)
                logger.warning(
                    "OpenAI API request timed out after %s seconds (attempt %s/%s). Retrying in %.1fs.",
                    self.timeout,
                    attempt,
                    self.max_retries,
                    delay,
                )
                if delay:
                    time.sleep(delay)
                continue
            except requests.RequestException as exc:  # pragma: no cover - network failure guard
                if attempt == self.max_retries:
                    logger.exception("Failed to contact OpenAI API")
                    raise AgentAPIError("Unable to contact OpenAI API") from exc

                delay = self._retry_delay(attempt)
                logger.warning(
                    "OpenAI API request failed (attempt %s/%s). Retrying in %.1fs.",
                    attempt,
                    self.max_retries,
                    delay,
                )
                if delay:
                    time.sleep(delay)
                continue

            if response.status_code in {429} or response.status_code >= 500:
                if attempt == self.max_retries:
                    try:
                        detail = response.json()
                    except ValueError:
                        detail = response.text
                    logger.error(
                        "OpenAI API error (%s): %s",
                        response.status_code,
                        detail,
                    )
                    raise AgentAPIError(
                        f"OpenAI API returned status {response.status_code}"
                    )

                delay = self._retry_delay(attempt)
                logger.warning(
                    "OpenAI API returned retryable status %s (attempt %s/%s). Retrying in %.1fs.",
                    response.status_code,
                    attempt,
                    self.max_retries,
                    delay,
                )
                if delay:
                    time.sleep(delay)
                continue
            break

        if response is None:
            raise AgentAPIError("Unable to contact OpenAI API")

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


class EducationSupportAgent(HealthSupportAgent):
    """AI agent focused exclusively on MSCC education and learning outcomes."""

    KEYWORD_TOPIC_MAP = {
        'education': {'education'},
        'learning': {'education'},
        'literacy': {'education'},
        'numeracy': {'education'},
        'grade': {'education'},
        'assessment': {'education'},
        'test': {'education'},
        'attendance': {'attendance'},
        'absent': {'attendance'},
        'presence': {'attendance'},
        'dropout': {'attendance'},
        'centre': {'location'},
        'center': {'location'},
        'location': {'location'},
        'governorate': {'location'},
        'life': {'life_quality'},
        'quality': {'life_quality'},
        'condition': {'life_quality'},
        'poverty': {'life_quality'},
        'vulnerability': {'life_quality'},
    }

    def __init__(
        self,
        api_key: str | None = None,
        model: str | None = None,
        base_url: str | None = None,
        timeout: int | None = None,
        max_retries: int | None = None,
        retry_backoff: float | None = None,
    ) -> None:
        education_model = model or getattr(
            settings,
            "OPENAI_EDUCATION_AGENT_MODEL",
            getattr(settings, "OPENAI_HEALTH_AGENT_MODEL", "gpt-4o-mini"),
        )
        super().__init__(
            api_key=api_key,
            model=education_model,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            retry_backoff=retry_backoff,
        )

    def _build_prompt(
        self,
        children_context: Sequence[dict],
        question: str | None = None,
        focus_topics: set[str] | None = None,
        keywords: Sequence[str] | None = None,
        programme_overview: dict | None = None,
    ) -> List[dict]:
        knowledge_engine = MSCCKnowledgeEngine(children_context)
        summary = knowledge_engine.render_compiled_summary() or json.dumps(
            children_context, indent=2, default=str
        )

        system_message = (
            "You are an education outcomes analyst supporting the MSCC (Makani) programme. "
            "Your job is to explain programme-wide learning results rather than individual cases."
        )
        user_instructions = (
            "Review only the education, learning, and grading information. Summarise trends across the "
            "full cohort: learning outcomes, assessment changes, attendance patterns, living conditions, "
            "and centre locations. Prioritise programme-wide conclusions and cohort signals over "
            "individual children. Recommend practical education follow-up steps at centre or cohort "
            "level, and flag data gaps that block an aggregated conclusion. Do not provide health or "
            "protection guidance; stay focused on education outcomes."
        )
        formatting = (
            "Return markdown with the sections 'Programme Learning Snapshot', 'Key Trends & Risks', "
            "and 'Centre & Cohort Actions'. Use counts, percentages, and comparisons to describe patterns. "
            "Refer to individual children only when necessary to illustrate a trend, and avoid listing "
            "registration ids unless strictly required for context. In all sections, rely on the aggregated "
            "overview data provided to keep the emphasis on overall insights rather than per-child follow-up."
        )

        focus_topics = set(focus_topics or [])
        question_text = (question or "").strip()
        keywords = [keyword for keyword in (keywords or []) if keyword]

        if question_text:
            user_instructions = f"{user_instructions}\n\nFocus specifically on: {question_text}"
        else:
            user_instructions = (
                f"{user_instructions}\n\nIf no question is provided, prioritise the strongest "
                "learning risks inferred from attendance, education assessments, and location trends, "
                "summarising them at programme level."
            )

        if keywords:
            detected = ", ".join(keywords)
            user_instructions = (
                f"{user_instructions}\n\nDetected question keywords: {detected}. Address these themes explicitly."
            )

        if focus_topics:
            topics_text = ", ".join(sorted(focus_topics))
            scope_instruction = (
                " Limit your response to the requested focus topics "
                f"({topics_text}) and avoid unrelated domains while keeping the discussion at "
                "programme or centre level."
            )
            if 'attendance' in focus_topics:
                scope_instruction += (
                    " Provide precise attendance rates and explain how they influence learning outcomes "
                    "for the wider cohort."
                )
            if 'location' in focus_topics:
                scope_instruction += (
                    " Compare centres and locations, noting where children face barriers or succeed "
                    "as groups."
                )
            if {'life_quality', 'vulnerability'} & focus_topics:
                scope_instruction += (
                    " Clarify how living conditions or vulnerability signals hinder learning progress "
                    "across the cohort."
                )
            user_instructions = f"{user_instructions}{scope_instruction}"

        overview_appendix = ""
        if programme_overview:
            try:
                overview_text = json.dumps(programme_overview, indent=2, default=str)
            except TypeError:
                overview_text = str(programme_overview)
            overview_appendix = (
                "\n\nAggregated programme overview (all eligible children before applying review limits):\n"
                f"{overview_text}"
            )

        messages = [
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": (
                    f"{user_instructions}\n\n{formatting}\n\nChildren data:\n{summary}{overview_appendix}"
                ),
            },
        ]
        return messages


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
    "EducationSupportAgent",
    "PreAssessmentAgent",
]
