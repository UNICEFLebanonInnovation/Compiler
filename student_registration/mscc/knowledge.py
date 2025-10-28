"""Helpers to compile MSCC knowledge snapshots for the AI agent."""

from __future__ import annotations

import hashlib
from collections import Counter
from dataclasses import dataclass
from datetime import datetime
from typing import List

from django.conf import settings
from django.db.models import Count, Exists, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.utils import timezone

from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.mscc import views as mscc_views
from student_registration.mscc.ai_agent import MSCCKnowledgeEngine
from student_registration.mscc.models import (
    EducationProgrammeAssessment,
    FollowUpService,
    HealthNutritionReferral,
    HealthNutritionService,
    MSCCKnowledgeSnapshot,
    ProvidedServices,
    PSSService,
    Registration,
)


@dataclass(frozen=True)
class KnowledgeCompilation:
    """Result returned after compiling MSCC knowledge."""

    generated_at: datetime
    summary: str
    documents: List[dict]
    children: List[dict]
    vulnerability_overview: dict


class MSCCKnowledgeCompiler:
    """Compile MSCC registrations into a shareable daily snapshot."""

    def __init__(self, limit: int | None = None) -> None:
        default_limit = getattr(settings, 'MSCC_KNOWLEDGE_SNAPSHOT_LIMIT', 200)
        self.limit = limit if limit is not None else default_limit

    def compile(self) -> KnowledgeCompilation:
        """Return the compiled knowledge result without persisting it."""

        children_context = self._build_children_context()
        engine = MSCCKnowledgeEngine(children_context)
        summary = engine.render_compiled_summary()
        documents = engine.documents
        enriched_children = engine.enriched_children
        vulnerability_overview = engine.vulnerability_overview
        generated_at = timezone.now()
        return KnowledgeCompilation(
            generated_at=generated_at,
            summary=summary,
            documents=documents,
            children=enriched_children,
            vulnerability_overview=vulnerability_overview,
        )

    def create_snapshot(self) -> MSCCKnowledgeSnapshot:
        """Compile the knowledge and persist it as a daily snapshot."""

        compilation = self.compile()
        digest = hashlib.sha256(compilation.summary.encode('utf-8')).hexdigest() if compilation.summary else None

        metadata = {
            'generated_at': compilation.generated_at.isoformat(),
            'children_count': len(compilation.children),
            'document_count': len(compilation.documents),
            'top_registration_ids': [
                child.get('registration_id')
                for child in compilation.children[:10]
                if child.get('registration_id') is not None
            ],
        }
        if digest:
            metadata['digest'] = digest

        if compilation.documents:
            metadata['document_index'] = [
                {
                    'registration_id': doc.get('registration_id'),
                    'child_id': doc.get('child_id'),
                    'tokens': sorted(doc.get('tokens') or []),
                    'numbers': sorted(doc.get('numbers') or []),
                    'vulnerability_severity': (doc.get('context') or {}).get('vulnerability_profile', {}).get('severity'),
                    'vulnerability_concerns': (doc.get('context') or {}).get('vulnerability_profile', {}).get('top_concerns', [])[:5],
                    'vulnerability_score': (doc.get('context') or {}).get('vulnerability_profile', {}).get('score'),
                }
                for doc in compilation.documents
            ]

            severity_counter: Counter[str] = Counter()
            domain_counter: Counter[str] = Counter()
            concern_counter: Counter[str] = Counter()
            for doc in compilation.documents:
                profile = (doc.get('context') or {}).get('vulnerability_profile') or {}
                severity = profile.get('severity') or 'unknown'
                severity_counter[severity] += 1
                for entry in profile.get('domain_breakdown') or []:
                    domain = entry.get('domain')
                    if domain:
                        domain_counter[domain] += 1
                for concern in profile.get('top_concerns') or []:
                    concern_counter[concern] += 1

            if severity_counter:
                metadata['vulnerability_severity'] = dict(
                    sorted(severity_counter.items(), key=lambda item: (-item[1], item[0]))
                )
            if domain_counter:
                metadata['vulnerability_domains'] = dict(
                    sorted(domain_counter.items(), key=lambda item: (-item[1], item[0]))
                )
            if concern_counter:
                metadata['top_vulnerability_concerns'] = [
                    {'concern': concern, 'count': count}
                    for concern, count in concern_counter.most_common(10)
                ]

        if compilation.vulnerability_overview:
            metadata['vulnerability_overview'] = compilation.vulnerability_overview

        snapshot, _ = MSCCKnowledgeSnapshot.objects.update_or_create(
            generated_for=compilation.generated_at.date(),
            defaults={
                'summary': compilation.summary,
                'children': compilation.children,
                'metadata': metadata,
                'document_count': len(compilation.documents),
            },
        )
        return snapshot

    def _build_children_context(self) -> List[dict]:
        queryset = Registration.objects.filter(
            deleted=False,
            type__in=['Core-Package', 'Core Package'],
        )

        pss_exists = PSSService.objects.filter(registration_id=OuterRef('pk'))
        health_service_exists = HealthNutritionService.objects.filter(registration_id=OuterRef('pk'))
        health_referral_exists = HealthNutritionReferral.objects.filter(registration_id=OuterRef('pk'))

        queryset = queryset.annotate(
            has_pss=Exists(pss_exists),
            has_health_service=Exists(health_service_exists),
            has_health_referral=Exists(health_referral_exists),
        ).filter(
            has_pss=True,
        ).filter(
            Q(has_health_service=True) | Q(has_health_referral=True)
        )

        absence_subquery = Subquery(
            MSCCAttendanceChild.objects.filter(
                registration_id=OuterRef('pk'),
                attended='No',
            ).values('registration_id').annotate(total=Count('id')).values('total'),
            output_field=IntegerField(),
        )
        pending_subquery = Subquery(
            ProvidedServices.objects.filter(
                registration_id=OuterRef('pk'),
                required=True,
                completed=False,
            ).values('registration_id').annotate(total=Count('id')).values('total'),
            output_field=IntegerField(),
        )

        queryset = queryset.annotate(
            absent_days=Coalesce(absence_subquery, 0, output_field=IntegerField()),
            pending_required=Coalesce(pending_subquery, 0, output_field=IntegerField()),
        ).order_by('-absent_days', '-pending_required', '-id')

        fetch_limit: int | None
        if self.limit:
            fetch_limit = max(self.limit * 3, self.limit)
        else:
            fetch_limit = None

        if fetch_limit:
            registrations = list(queryset.select_related('child', 'round')[:fetch_limit])
        else:
            registrations = list(queryset.select_related('child', 'round'))

        if not registrations:
            return []

        registration_ids = [registration.id for registration in registrations]
        child_ids = [registration.child_id for registration in registrations if registration.child_id]

        services_map: dict[int, list] = {}
        for service in ProvidedServices.objects.filter(registration_id__in=registration_ids):
            services_map.setdefault(service.registration_id, []).append(service)

        attendance_map: dict[int, list] = {}
        attendance_qs = MSCCAttendanceChild.objects.filter(
            registration_id__in=registration_ids
        ).select_related('attendance_day').order_by('attendance_day__attendance_date', 'id')
        for attendance in attendance_qs:
            attendance_map.setdefault(attendance.registration_id, []).append(attendance)

        pss_map: dict[int, PSSService] = {}
        for pss in PSSService.objects.filter(registration_id__in=registration_ids).order_by('-id'):
            pss_map.setdefault(pss.registration_id, pss)

        health_service_map: dict[int, HealthNutritionService] = {}
        for health_service in HealthNutritionService.objects.filter(registration_id__in=registration_ids).order_by('-id'):
            health_service_map.setdefault(health_service.registration_id, health_service)

        health_referral_map: dict[int, HealthNutritionReferral] = {}
        for health_referral in HealthNutritionReferral.objects.filter(registration_id__in=registration_ids).order_by('-id'):
            health_referral_map.setdefault(health_referral.registration_id, health_referral)

        followup_map: dict[int, list] = {}
        followup_qs = (
            FollowUpService.objects.filter(registration_id__in=registration_ids)
            .order_by('created', 'id')
        )
        for followup in followup_qs:
            followup_map.setdefault(followup.registration_id, []).append(followup)

        education_assessment_map: dict[int, EducationProgrammeAssessment] = {}
        education_qs = (
            EducationProgrammeAssessment.objects.filter(registration_id__in=registration_ids)
            .order_by('-modified', '-id')
        )
        for education_assessment in education_qs:
            education_assessment_map.setdefault(education_assessment.registration_id, education_assessment)

        registration_history_map: dict[int, List[Registration]] = {}
        if child_ids:
            history_qs = (
                Registration.objects.filter(child_id__in=child_ids, deleted=False)
                .select_related('round', 'center')
                .order_by('child_id', 'registration_date', 'created', 'id')
            )
            for history_record in history_qs:
                registration_history_map.setdefault(history_record.child_id, []).append(history_record)

        children_context = [
            mscc_views._build_child_context(
                registration,
                services_map.get(registration.id, []),
                attendance_map.get(registration.id, []),
                pss_map.get(registration.id),
                health_service_map.get(registration.id),
                health_referral_map.get(registration.id),
                followup_map.get(registration.id, []),
                education_assessment_map.get(registration.id),
                registration_history=registration_history_map.get(registration.child_id, []),
            )
            for registration in registrations
        ]

        children_context.sort(key=lambda child: child.get('risk_score') or 0, reverse=True)
        if self.limit:
            children_context = children_context[: self.limit]
        return children_context


__all__ = ['MSCCKnowledgeCompiler', 'KnowledgeCompilation']
