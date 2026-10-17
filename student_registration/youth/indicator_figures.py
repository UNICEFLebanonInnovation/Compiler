"""Youth indicator figures: how many young people each indicator reached, for NeuroDB.

The youth module records every enrolment of a registered youth in a programme under a master
indicator (MasterProgram) and a sub indicator (SubProgram), with the partner, the donor, the
programme document and the place. This module turns those enrolments into counts of unique young
people, so that partners, donors and UNICEF can report without re-counting by hand.

Only counts leave this module: no name, no identifier, no row about a person.

Which registrations count (format 2) is what the Youth Power BI dashboard reads, the view
``vw_youth_data_all`` (see student_registration/figures/power_bi.py):

* view mode: exactly the registrations of the view for the period, deleted ones left out (setting
  ``FIGURES_POWER_BI['youth']['deleted']``), with the partner the view gives each registration. The
  view's definition lives only in production, so its key column (``registration_id``, else ``id``) and
  its period column (``year_id``, else ``year``, else the registration's own year) are found when
  counting;
* rule mode, when the view cannot be used (missing, not readable, its key is not the registration id,
  empty for a period that has registrations, or the setting says so): the registrations not deleted of
  the year.

The period is a reporting year (``Year``) or ``"all"``: every year, registrations without a year
included (those saved before September 2025 have none, and were in no year before).

``figures`` keeps its meaning: unique young people with an enrolment under a master indicator. A
young person enrolled twice under the same indicator counts once, and a young person enrolled under
two indicators counts once in their master indicator's total. Unique counts cannot be added up across
groups (the same person can be in two partners' programmes), so the figures are given for a fixed set
of groupings ("grouping sets") and a reader picks the one that matches its question: every combination
of master indicator, partner, donor and governorate, each alone or with one more detail (sub indicator,
programme document, district, sex, age group or nationality), and the sub indicators of each programme
document.

``blocks`` (format 2), counted in the database (figures/engine.py, read only):

* ``registered``: every counted registration, with or without an enrolment, by partner and the
  youth's home address, sex, age group and nationality: unique young people, registrations, and the
  young people among them enrolled under a master indicator;
* ``enrolments``: the enrolment rows under a master indicator (a youth enrolled twice counts twice),
  beside the unique young people, by indicator, programme document, partner, donor and place.

Places: the enrolment's governorate and district, or the youth's registered address when the
enrolment is "in the same location" (the form leaves the enrolment's place empty then); ``registered``
uses the address. Partner: the registration's, else the programme document's (``registered``: the
registration's); in view mode, the view's. Age: the reporting year minus the birth year (for "all",
the current reporting year).

``power_bi`` says which way the registrations were chosen and why, and reconciles in counts the view,
this count and what NeuroDB counted before (the registrations of the year with an enrolment under a
master indicator).
"""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

from django.db.models import Case, CharField, Exists, F, Func, IntegerField, OuterRef, Q, Value, When
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone

from student_registration.figures import education, engine
from student_registration.locations.models import Location

from .models import (
    Donor,
    EnrolledPrograms,
    MasterProgram,
    ProgramDocument,
    ProgramDocumentIndicator,
    Registration,
    SubProgram,
    Year,
)

FORMAT_VERSION = 2
ALL = 'all'  # the period of every year, registrations without a year included

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

# the blocks (format 2)
REGISTERED = ('partner', 'home_governorate', 'home_district', 'sex', 'age_group', 'nationality')
REGISTERED_MEASURES = (
    ('people', 'COUNT(DISTINCT b.person)'),
    ('registrations', 'COUNT(*)'),
    ('enrolled_people', 'COUNT(DISTINCT b.person) FILTER (WHERE b.enrolled = 1)'),
)
ENROLMENTS = ('master', 'sub', 'program_document', 'partner', 'donor', 'governorate')
ENROLMENT_GROUPINGS = ((), ('master',), ('master', 'sub'), ('program_document', 'sub'), ('partner',),
                       ('master', 'partner'), ('donor',), ('governorate',))
ENROLMENT_MEASURES = (('enrolments', 'COUNT(*)'), ('people', 'COUNT(DISTINCT b.person)'))


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


def age_group_sql(path: str, year: int):
    """``age_group`` as SQL: (the birth year, the age group); the caller annotates the first as "_born"."""
    digits = Func(F(path), Value('[^0-9]'), Value(''), Value('g'), function='REGEXP_REPLACE',
                  output_field=CharField())
    born = Case(When(**{path + '__regex': r'^[[:space:]]*[0-9]{1,9}[[:space:]]*$'},
                     then=Cast(digits, IntegerField())), default=None, output_field=IntegerField())
    whens = [When(_born__isnull=True, then=Value(NOT_SPECIFIED)),
             When(_born__lt=1900, then=Value(NOT_SPECIFIED)),
             When(_born__gt=year, then=Value(NOT_SPECIFIED))]
    whens += [When(_born__gte=year - high, then=Value(label)) for _low, high, label in AGE_GROUPS]
    return born, Case(*whens, default=Value(NOT_SPECIFIED), output_field=CharField())


def sex_of(gender) -> str:
    return gender if gender in ('Male', 'Female') else NOT_SPECIFIED


def resolve_year(name: str | None) -> Year | None:
    """The reporting year asked for, else the current one."""
    if name:
        return Year.objects.filter(name=str(name).strip()).first()
    return Year.objects.filter(current_year=True).first()


def current_year_name() -> str | None:
    """The reporting year flagged current, else the latest one."""
    year = Year.objects.filter(current_year=True).first() or Year.objects.order_by('-name').first()
    return year.name if year else None


def reporting_year(year: Year | None) -> int:
    """The calendar year ages are counted in: the year's own; for "all", the current year's."""
    name = year.name if year is not None else (current_year_name() or '')
    return int(name[:4]) if name[:4].isdigit() else timezone.localdate().year


# ----------------------------------------------------------------------------- which rows count
def rule(year: Year | None):
    """Compiler's own rule (rule mode): the registrations not deleted of ``year`` (None: every year)."""
    registrations = Registration.objects.filter(deleted=False)
    return registrations.filter(year=year) if year is not None else registrations


def before(year: Year | None):
    """What NeuroDB counted before the Power BI alignment (for the reconciliation only): the registrations
    not deleted of ``year`` with an enrolment under a master indicator. There was no "all" period; for it,
    the registrations that were in some year (those without a year were in none)."""
    enrolled = EnrolledPrograms.objects.filter(registration=OuterRef('pk'), master_program__isnull=False)
    registrations = Registration.objects.filter(Exists(enrolled), deleted=False)
    return registrations.filter(year=year) if year is not None else registrations.filter(year__isnull=False)


def counted(year: Year | None, population):
    """The registrations this payload counts. View mode: the view's (the population joins them in),
    deleted ones left out unless the setting keeps them; rule mode: ``rule``."""
    if population.joined:
        if population.deleted == 'exclude':
            return Registration.objects.filter(deleted=False)
        return Registration.objects.all()
    return rule(year)


def population_of(year: Year | None):
    """The view's population for the period (power_bi.population), never failing the count."""
    return education.view_population('youth', year.name if year is not None else ALL, year=year,
                                     rule=rule(year))


def _enrolment_rows(year: Year | None, population, alias: str):
    """The enrolments under a master indicator of the counted registrations (in view mode, the
    population's join restricts them to the view's)."""
    enrolments = EnrolledPrograms.objects.using(alias).filter(registration__isnull=False,
                                                              master_program__isnull=False)
    if population.joined:
        if population.deleted == 'exclude':
            enrolments = enrolments.filter(registration__deleted=False)
        return enrolments
    enrolments = enrolments.filter(registration__deleted=False)
    return enrolments.filter(registration__year=year) if year is not None else enrolments


def _enrolments(year: Year | None, population, alias: str):
    enrolments = _enrolment_rows(year, population, alias)
    if population.joined:  # the view's registrations, held as an array
        enrolments = enrolments.filter(
            registration_id__in=RawSQL('SELECT unnest(%s::int[])', [population.arrays()[0]]))
    return (
        enrolments
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


def _figures(year: Year | None, population, alias: str, year_number: int):
    """The unique young people per grouping (one pass over the enrolments), and the ids each dimension
    refers to."""
    grouping_list = groupings()
    people: dict[tuple, dict[tuple, set]] = {g: defaultdict(set) for g in grouping_list}
    seen = defaultdict(set)  # the ids each dimension refers to, to describe them below
    view_partner = None  # view mode: the partner the view gives each registration
    if population.joined and 'partner' in population.overrides:
        view_partner = dict(zip(population.ids, population.overrides['partner']))

    # read a chunk at a time, the parameters (in view mode, the view's registration ids) bound on the server
    sql, params = _enrolments(year, population, alias).query.sql_with_params()
    for (
        registration_id, adolescent_id, master_id, sub_id, donor_id, pd_id, partner_id, pd_partner_id,
        gov_id, district_id, home_gov_id, home_district_id, gender, birthday_year, nationality_id,
    ) in engine.stream(sql, params):
        person = adolescent_id or ('r', registration_id)
        if not gov_id:  # "same location": the youth's registered address
            gov_id, district_id = home_gov_id, home_district_id
        if view_partner is not None:
            partner = view_partner.get(registration_id)
        else:
            partner = partner_id or pd_partner_id
        values = {
            'master': master_id,
            'sub': sub_id,
            'partner': partner,
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
    return figures, seen


def _blocks(year: Year | None, population, alias: str, year_number: int) -> dict:
    """The ``registered`` and ``enrolments`` blocks, each counted in one read-only query."""
    enrolled = EnrolledPrograms.objects.filter(registration=OuterRef('pk'), master_program__isnull=False)
    born, age = age_group_sql('adolescent__birthday_year', year_number)
    fields = {
        # a registration without a youth record counts as its own person (never an adolescent id)
        'person': Coalesce(F('adolescent_id'), F('id') * Value(-1), output_field=IntegerField()),
        'partner': F('partner_id'),
        'home_governorate': F('adolescent__governorate_id'),
        'home_district': F('adolescent__district_id'),
        'sex': education.sex('adolescent__gender'),
        '_born': born,
        'age_group': age,
        'nationality': F('adolescent__nationality_id'),
        'enrolled': Case(When(Exists(enrolled), then=Value(1)), default=Value(0), output_field=IntegerField()),
    }
    blocks = {'registered': education.block(
        'registered', education.select(counted(year, population).using(alias), fields, population), REGISTERED,
        engine.groupings(('partner', 'home_governorate'), ('sex', 'age_group', 'nationality', 'home_district')),
        REGISTERED_MEASURES)}

    fields = {
        'person': Coalesce(F('registration__adolescent_id'), F('registration_id') * Value(-1),
                           output_field=IntegerField()),
        'master': F('master_program_id'),
        'sub': F('sub_program_id'),
        'program_document': F('program_document_id'),
        'partner': Coalesce(F('registration__partner_id'), F('program_document__partner_id'),
                            output_field=IntegerField()),
        'donor': F('donor_id'),
        'governorate': Coalesce(F('governorate_id'), F('registration__adolescent__governorate_id'),
                                output_field=IntegerField()),
    }
    blocks['enrolments'] = education.block(
        'enrolments', education.select(_enrolment_rows(year, population, alias), fields, population,
                                       rid='registration_id'),
        ENROLMENTS, engine.groupings((), (), ENROLMENT_GROUPINGS), ENROLMENT_MEASURES)
    return blocks


def build(year: Year | None, alias: str | None = None, population=None) -> dict:
    """The figures of ``year`` (None: every year, the "all" period; see the module docstring), ready to
    serialise as JSON. ``alias``: the database the ORM reads (default: the figures database; inside
    ``engine.read_only_transaction()``, the alias it yields); ``population``: the view's for the period
    (found when None)."""
    alias = alias or engine.database_alias()
    period = year.name if year is not None else ALL
    year_number = reporting_year(year)
    if population is None:
        population = population_of(year)

    figures, seen = _figures(year, population, alias, year_number)
    blocks = _blocks(year, population, alias, year_number)
    power = education.power_bi_block(
        'youth', period, population, before(year), counted(year, population),
        current=year is not None and year.name == current_year_name(),
        period_rule='year' if year is not None else ALL)

    for name in ('partner', 'nationality', 'program_document', 'donor', 'master', 'sub'):
        seen[name] |= education.ids_in(blocks, name)
    places = set(seen['governorate']) | seen['district']
    for name in ('governorate', 'home_governorate', 'home_district'):
        places |= education.ids_in(blocks, name)
    return {
        'format': FORMAT_VERSION,
        'year': period,
        'generated_at': timezone.now().isoformat(),
        'counts': 'unique young people (not enrolments), per grouping',
        'indicators': _indicators(seen, year, alias),
        'partners': _partners(seen['partner'], alias),
        'donors': list(Donor.objects.using(alias).filter(id__in=seen['donor']).values('id', 'name')),
        'program_documents': _program_documents(seen['program_document'], year, alias),
        'targets': _targets(year, alias),
        'locations': _locations(places, alias),
        'nationalities': _nationalities(seen['nationality'], alias),
        'figures': figures,
        'blocks': blocks,
        'power_bi': power,
    }


def _year_targets(year: Year | None, alias: str):
    """The programme document indicators of ``year``; none for "all" (targets of different years do not
    add up)."""
    targets = ProgramDocumentIndicator.objects.using(alias)
    return targets.filter(program_document__year=year) if year is not None else targets.none()


def _indicators(seen, year: Year | None, alias: str) -> list[dict]:
    """The master and sub indicators the enrolments or the year's programme documents refer to."""
    targets = _year_targets(year, alias)
    master_ids = set(seen['master']) | set(targets.exclude(master_indicator=None).values_list(
        'master_indicator_id', flat=True))
    sub_ids = set(seen['sub']) | set(targets.exclude(sub_indicator=None).values_list(
        'sub_indicator_id', flat=True))
    out = [
        {'id': m.id, 'level': 'master', 'number': m.number, 'name': m.name, 'master': None,
         'active': m.active}
        for m in MasterProgram.objects.using(alias).filter(id__in=master_ids).order_by('number', 'name')
    ]
    out += [
        {'id': s.id, 'level': 'sub', 'number': s.number, 'name': s.name, 'master': s.master_program_id,
         'active': None}
        for s in SubProgram.objects.using(alias).filter(id__in=sub_ids).order_by('number', 'name')
    ]
    return out


def _partners(ids, alias: str) -> list[dict]:
    from student_registration.schools.models import PartnerOrganization

    return list(PartnerOrganization.objects.using(alias).filter(id__in=ids).values('id', 'name', 'short_name'))


def _program_documents(ids, year: Year | None, alias: str) -> list[dict]:
    """The programme documents referred to and, for a year, every programme document of the year."""
    chosen = Q(id__in=set(ids))
    if year is not None:
        chosen |= Q(year=year)
    documents = ProgramDocument.objects.using(alias).filter(chosen).distinct()
    out = []
    for pd in documents.select_related('year').prefetch_related('donors', 'governorates'):
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


def _targets(year: Year | None, alias: str) -> list[dict]:
    return [
        {
            'program_document': t.program_document_id,
            'master': t.master_indicator_id,
            'sub': t.sub_indicator_id,
            'baseline': t.baseline,
            'target': t.target,
        }
        for t in _year_targets(year, alias).order_by('id')
    ]


def _locations(ids, alias: str) -> list[dict]:
    return [
        {'id': loc.id, 'name': loc.name_en or loc.name, 'p_code': loc.p_code, 'parent': loc.parent_id,
         'type': loc.type.name if loc.type_id else None}
        for loc in Location.objects.using(alias).filter(id__in=ids).select_related('type')
    ]


def _nationalities(ids, alias: str) -> list[dict]:
    from student_registration.students.models import Nationality

    return [
        {'id': n.id, 'name': n.name_en or n.name}
        for n in Nationality.objects.using(alias).filter(id__in=ids)
    ]
