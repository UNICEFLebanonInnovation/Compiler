"""Youth indicator figures: how many young people each indicator reached, for NeuroDB.

The youth module records every enrolment of a registered youth in a programme under a master
indicator (MasterProgram) and a sub indicator (SubProgram), with the partner, the donor, the
programme document and the place. This module turns those enrolments into counts of unique young
people, so that partners, donors and UNICEF can report without re-counting by hand.

Only counts leave this module: no name, no identifier, no row about a person.

A young person enrolled twice under the same indicator counts once, and a young person enrolled
under two indicators counts once in their master indicator's total. Unique counts cannot be added
up across groups (the same person can be in two partners' programmes), so the figures are given for
a fixed set of groupings ("grouping sets") and a reader picks the one that matches its question:
every combination of master indicator, partner, donor and governorate, each alone or with one more
detail (sub indicator, programme document, district, sex, age group or nationality), and the sub
indicators of each programme document.

Places: the enrolment's governorate and district, or the youth's registered address when the
enrolment is "in the same location" (the form leaves the enrolment's place empty then).
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from django.utils import timezone

from student_registration.locations.models import Location

from .models import (
    Donor,
    EnrolledPrograms,
    MasterProgram,
    ProgramDocument,
    ProgramDocumentIndicator,
    SubProgram,
    Year,
)

FORMAT_VERSION = 1

# The groupings: every subset of the main dimensions, alone or with one detail.
MAIN_DIMENSIONS = ('master', 'partner', 'donor', 'governorate')
DETAILS = ('sub', 'program_document', 'district', 'sex', 'age_group', 'nationality')
# Also: youth per sub indicator of each programme document, to compare with the partner's reporting
EXTRA_GROUPINGS = (('program_document', 'sub'),)

AGE_GROUPS = (
    (0, 14, 'Under 15'),
    (15, 17, '15-17'),
    (18, 24, '18-24'),
    (25, 200, '25 and over'),
)
NOT_SPECIFIED = 'Not specified'


def groupings() -> list[tuple[str, ...]]:
    """Every grouping the figures are given for, each a sorted tuple of dimension names."""
    out = []
    for size in range(len(MAIN_DIMENSIONS) + 1):
        for main in combinations(MAIN_DIMENSIONS, size):
            out.append(tuple(sorted(main)))
            for detail in DETAILS:
                out.append(tuple(sorted(main + (detail,))))
    return out + [tuple(sorted(g)) for g in EXTRA_GROUPINGS]


def age_group(birthday_year, year: int) -> str:
    """The youth's age group in the reporting year, from the birth year alone."""
    try:
        born = int(birthday_year or 0)
    except (TypeError, ValueError):
        return NOT_SPECIFIED
    if born < 1900:
        return NOT_SPECIFIED
    age = year - born
    for low, high, label in AGE_GROUPS:
        if low <= age <= high:
            return label
    return NOT_SPECIFIED


def sex_of(gender) -> str:
    return gender if gender in ('Male', 'Female') else NOT_SPECIFIED


def resolve_year(name: str | None) -> Year | None:
    """The reporting year asked for, else the current one."""
    if name:
        return Year.objects.filter(name=str(name).strip()).first()
    return Year.objects.filter(current_year=True).first()


def _enrolments(year: Year):
    return (
        EnrolledPrograms.objects.filter(
            registration__isnull=False,
            registration__deleted=False,
            registration__year=year,
            master_program__isnull=False,
        )
        .order_by()
        .values_list(
            'registration_id',
            'registration__adolescent_id',
            'master_program_id',
            'sub_program_id',
            'donor_id',
            'program_document_id',
            'registration__partner_id',
            'program_document__partner_id',
            'governorate_id',
            'district_id',
            'registration__adolescent__governorate_id',
            'registration__adolescent__district_id',
            'registration__adolescent__gender',
            'registration__adolescent__birthday_year',
            'registration__adolescent__nationality_id',
        )
    )


def build(year: Year) -> dict:
    """The figures of ``year`` (see the module docstring), ready to serialise as JSON."""
    year_number = int(year.name[:4]) if year.name[:4].isdigit() else timezone.localdate().year
    grouping_list = groupings()
    people: dict[tuple, dict[tuple, set]] = {g: defaultdict(set) for g in grouping_list}
    seen = defaultdict(set)  # the ids each dimension refers to, to describe them below

    for (
        registration_id, adolescent_id, master_id, sub_id, donor_id, pd_id, partner_id, pd_partner_id,
        gov_id, district_id, home_gov_id, home_district_id, gender, birthday_year, nationality_id,
    ) in _enrolments(year).iterator(chunk_size=5000):
        person = adolescent_id or ('r', registration_id)
        if not gov_id:  # "same location": the youth's registered address
            gov_id, district_id = home_gov_id, home_district_id
        values = {
            'master': master_id,
            'sub': sub_id,
            'partner': partner_id or pd_partner_id,
            'donor': donor_id,
            'program_document': pd_id,
            'governorate': gov_id,
            'district': district_id,
            'sex': sex_of(gender),
            'age_group': age_group(birthday_year, year_number),
            'nationality': nationality_id,
        }
        for name in ('master', 'sub', 'partner', 'donor', 'program_document', 'governorate', 'district',
                     'nationality'):
            if values[name]:
                seen[name].add(values[name])
        for grouping in grouping_list:
            people[grouping][tuple(values[d] for d in grouping)].add(person)

    figures = [
        {
            'by': list(grouping),
            'rows': [list(key) + [len(persons)] for key, persons in sorted(
                cells.items(), key=lambda item: tuple('' if v is None else str(v) for v in item[0])
            )],
        }
        for grouping, cells in people.items()
    ]
    return {
        'format': FORMAT_VERSION,
        'year': year.name,
        'generated_at': timezone.now().isoformat(),
        'counts': 'unique young people (not enrolments), per grouping',
        'indicators': _indicators(seen, year),
        'partners': _partners(seen['partner']),
        'donors': list(Donor.objects.filter(id__in=seen['donor']).values('id', 'name')),
        'program_documents': _program_documents(seen['program_document'], year),
        'targets': _targets(year),
        'locations': _locations(seen['governorate'] | seen['district']),
        'nationalities': _nationalities(seen['nationality']),
        'figures': figures,
    }


def _indicators(seen, year: Year) -> list[dict]:
    """The master and sub indicators the enrolments or the year's programme documents refer to."""
    targets = ProgramDocumentIndicator.objects.filter(program_document__year=year)
    master_ids = set(seen['master']) | set(targets.exclude(master_indicator=None).values_list(
        'master_indicator_id', flat=True))
    sub_ids = set(seen['sub']) | set(targets.exclude(sub_indicator=None).values_list(
        'sub_indicator_id', flat=True))
    out = [
        {'id': m.id, 'level': 'master', 'number': m.number, 'name': m.name, 'master': None,
         'active': m.active}
        for m in MasterProgram.objects.filter(id__in=master_ids).order_by('number', 'name')
    ]
    out += [
        {'id': s.id, 'level': 'sub', 'number': s.number, 'name': s.name, 'master': s.master_program_id,
         'active': None}
        for s in SubProgram.objects.filter(id__in=sub_ids).order_by('number', 'name')
    ]
    return out


def _partners(ids) -> list[dict]:
    from student_registration.schools.models import PartnerOrganization

    return list(PartnerOrganization.objects.filter(id__in=ids).values('id', 'name', 'short_name'))


def _program_documents(ids, year: Year) -> list[dict]:
    documents = ProgramDocument.objects.filter(id__in=set(ids)) | ProgramDocument.objects.filter(year=year)
    out = []
    for pd in documents.distinct().prefetch_related('donors', 'governorates'):
        out.append({
            'id': pd.id,
            'project_code': (pd.project_code or '').strip(),
            'project_name': pd.project_name,
            'partner': pd.partner_id,
            'year': pd.year.name if pd.year_id else None,
            'start_date': pd.start_date.isoformat() if pd.start_date else None,
            'end_date': pd.end_date.isoformat() if pd.end_date else None,
            'donors': sorted(d.id for d in pd.donors.all()),
            'governorates': sorted(g.id for g in pd.governorates.all()),
        })
    return out


def _targets(year: Year) -> list[dict]:
    return [
        {
            'program_document': t.program_document_id,
            'master': t.master_indicator_id,
            'sub': t.sub_indicator_id,
            'baseline': t.baseline,
            'target': t.target,
        }
        for t in ProgramDocumentIndicator.objects.filter(program_document__year=year).order_by('id')
    ]


def _locations(ids) -> list[dict]:
    return [
        {'id': loc.id, 'name': loc.name_en or loc.name, 'p_code': loc.p_code, 'parent': loc.parent_id,
         'type': loc.type.name if loc.type_id else None}
        for loc in Location.objects.filter(id__in=ids).select_related('type')
    ]


def _nationalities(ids) -> list[dict]:
    from student_registration.students.models import Nationality

    return [
        {'id': n.id, 'name': n.name_en or n.name}
        for n in Nationality.objects.filter(id__in=ids)
    ]
