"""The education programmes' figures for NeuroDB: Makani (MSCC) and Bridging (Dirasa).

Counts only. For each programme and reporting period the payload holds several blocks, each a set
of groupings (see engine.py) with its measures:

* ``registrations``: unique children registered (not deleted), by partner, governorate, district,
  cadaster, center or school, sex, age group, nationality, disability and the programme's own
  categories (registration type, level, education status, learning result, source of
  identification...). Bridging also counts the children pre-tested and post-tested;
* ``services``: unique children per service received (Makani: one row per service record; Bridging:
  the "yes" answers of the services form);
* ``education_programmes`` (Makani): unique children per education programme (BLN, ABLN, CBECE...);
* ``sites``: centers (Makani) or schools (Bridging) with at least one child registered;
* ``staff``: facilitators (Makani) or teachers (Bridging);
* ``attendance``: attendance days recorded and attended (not unique children), by month.

The payload also holds ``cubes`` (format 2): records counted per combination of all the dashboard's
slicers at once (see ``engine.cube``), so NeuroDB can filter on any of them and add the rows up.

* Makani: ``enrolment`` (registrations, with the cards' flags: married, IDP, caregiver counselling,
  and the answers of the latest health and nutrition record) and ``staff`` (today's facilitators);
  ``centers`` lists their centers with type, emergency status and GPS point;
* Bridging: ``enrolment`` (registrations), ``teachers`` and ``trainings`` (teachers per training
  topic); ``schools`` lists their schools with the children numbers the schools report;
  ``outreach`` counts the Kobo outreach children of every year (shared by all programmes) per
  answer of four questions.

The period of both programmes is a year (format 4). Makani's: the rounds whose year is Y (or the rounds
flagged current, setting ``period``). Bridging's: the CLM rounds whose Bridging start date is in Y, a round
without one by the first year in its name (``power_bi.bridging_year``; or the Bridging rounds flagged
current, setting ``period``). A child counts once per year however many rounds of the year; registrations
add up over the rounds; the ``round`` dimension of Bridging's cubes and registrations block still shows one
round of the year.

Which registrations count (format 3) is what the Power BI dashboards read (power_bi.py):

* view mode: exactly the registrations of the Power BI view (``vw_mscc_data``, ``vw_bridging_data``)
  for the period (Makani: the rows whose round is a round of the year; Bridging: the rows whose round is a
  round of the year, or of the year by the view's own year column), deleted ones left out (setting
  ``FIGURES_POWER_BI[...]['deleted']``), with the partner and the centre or school the view gives each
  registration. The view decides everything else (TLS, rounds...);
* rule mode, when the view cannot be used (missing, not readable, its key is not the registration id,
  empty for a period that has registrations, or the setting says so): Compiler's own rule. Makani,
  registrations not deleted, with a child, in a round of the year, TLS left out (TLS has its own views)
  and registrations without a round left out (they are in neither dashboard; ``pending_round`` counts
  them in the current year); Bridging, registrations not deleted, in a round of the year, with a student.

The payload's ``power_bi`` part says which mode counted and why, and reconciles the two in counts. A child
who dropped out still counts as reached; the learning result shows the dropouts. A child is counted once
per figure, however many services, records or partners. The staff, teachers and trainings counts and the
attendance are not in the views and keep their own rules.
"""

from __future__ import annotations

import datetime
import logging

from django.db.models import (
    Case,
    CharField,
    Exists,
    F,
    Func,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.expressions import RawSQL
from django.db.models.functions import Cast, Coalesce, Left, Lower, NullIf, Trim
from django.utils import timezone

from . import engine, power_bi

logger = logging.getLogger(__name__)

FORMAT_VERSION = 4  # 4: Dirasa per year (the rounds of the year); Makani's payload unchanged
NOT_SPECIFIED = 'Not specified'
AGE_GROUPS = ('Under 6', '6-9', '10-14', '15-17', '18 and over', NOT_SPECIFIED)
LEBANON = ((33.0, 34.8), (35.0, 36.7))  # rough box of the GPS points kept: latitude, longitude


# ---------------------------------------------------------------------------------------- helpers
def sex(path):
    return Case(
        When(**{path: 'Male'}, then=Value('Male')),
        When(**{path: 'Female'}, then=Value('Female')),
        default=Value(NOT_SPECIFIED),
        output_field=CharField(),
    )


def yes_no(path):
    """'Yes', 'No' or "Not specified" from a yes/no answer, whatever its case."""
    return Case(
        When(**{path + '__iexact': 'yes'}, then=Value('Yes')),
        When(**{path + '__iexact': 'no'}, then=Value('No')),
        default=Value(NOT_SPECIFIED),
        output_field=CharField(),
    )


def caregiver(path):
    return Case(
        When(**{path + '__iexact': 'mother'}, then=Value('Mother')),
        When(**{path + '__iexact': 'father'}, then=Value('Father')),
        When(**{path + '__iexact': 'other'}, then=Value('Other')),
        default=Value(NOT_SPECIFIED),
        output_field=CharField(),
    )


def blank_to_null(expression):
    return NullIf(expression, Value(''))


def latest(model, value, path='registration'):
    """``value`` (a field name or an expression) of the latest ``model`` record (highest id) of each
    registration, NULL when it has none."""
    value = F(value) if isinstance(value, str) else value
    records = model.objects.filter(**{path: OuterRef('pk')}).order_by('-id')
    return Subquery(records.values(v=value)[:1])


def text_key(path):
    """A free-text answer as a key: lower case, every run of other characters as one "_", cut at 40
    characters (older Kobo forms cut their names there), no "_" at either end, NULL when blank. The
    name and the label of a Kobo choice ("never_been_engaged_in_any_type_of_learni", "Never been
    engaged in any type of learning") give the same key. The leading "_" goes before the cut, so a
    quote, dash or tab in front of the answer does not shorten its key."""
    underscored = Func(Lower(Trim(path)), Value('[^a-z0-9]+'), Value('_'), Value('g'),
                       function='REGEXP_REPLACE', output_field=CharField())
    leading = Func(underscored, Value('_'), function='LTRIM', output_field=CharField())
    return blank_to_null(Func(Left(leading, 40), Value('_'), function='RTRIM', output_field=CharField()))


def month_of(date_path):
    """``"2025-03"``: the month of a date, as text."""
    return Func(F(date_path), Value('YYYY-MM'), function='to_char', output_field=CharField())


def age_group(birthday_year_path, year):
    """The age group in ``year`` from a four-digit birth year stored as text (else "Not specified")."""
    born = Case(
        When(**{birthday_year_path + '__regex': r'^[0-9]{4}$'},
             then=Cast(birthday_year_path, IntegerField())),
        default=None,
        output_field=IntegerField(),
    )
    ages = ((6, 'Under 6'), (10, '6-9'), (15, '10-14'), (18, '15-17'))
    whens = [When(_born__isnull=True, then=Value(NOT_SPECIFIED)),
             When(_born__gt=year, then=Value(NOT_SPECIFIED)),
             When(_born__lt=1900, then=Value(NOT_SPECIFIED))]
    whens += [When(_born__gt=year - limit, then=Value(label)) for limit, label in ages]
    return born, Case(*whens, default=Value('18 and over'), output_field=CharField())


RID = 'x_pbi_rid'  # the registration id selected for the join with the view's population


def _annotate(queryset, fields, rid=None):
    """Annotate ``fields`` (name -> expression) under prefixed names: an annotation may not share a
    model field's name. Names starting with "_" are helpers (kept as they are, not selected). ``rid``:
    the path to the registration id, also selected (as RID) for the join with the view."""
    for name, expression in fields.items():
        queryset = queryset.annotate(**{(name if name.startswith('_') else 'x_' + name): expression})
    names = ['x_' + n for n in fields if not n.startswith('_')]
    if rid is not None:
        queryset = queryset.annotate(**{RID: F(rid)})
        names.append(RID)
    return queryset.order_by().values(*names)


def _renamed(sql, params, fields, population=None, overrides=None):
    """The renamed columns. With a view population: only the view's registrations of the period (a join
    with its ids, held as arrays), each with its view rows (``view_rows``), and the dimensions the view
    gives (partner, centre or school) taken from the view; ``overrides`` maps other column names to them
    (e.g. ``{'person': 'center'}``)."""
    names = [n for n in fields if not n.startswith('_')]
    if population is None:
        return 'SELECT %s FROM (%s) AS r' % (', '.join('r.x_%s AS %s' % (n, n) for n in names), sql), params
    dims = list(population.overrides)
    taken = {d: d for d in dims}
    taken.update({n: d for n, d in (overrides or {}).items() if d in dims})
    columns = ['pv.%s AS %s' % (taken[n], n) if n in taken else 'r.x_%s AS %s' % (n, n) for n in names]
    columns.append('pv.n AS view_rows')
    sql = 'SELECT %s FROM (%s) AS r JOIN unnest(%s) AS pv(%s) ON pv.id = r.%s' % (
        ', '.join(columns), sql, ', '.join(['%s::int[]'] * (2 + len(dims))), ', '.join(['id', 'n'] + dims), RID)
    return sql, list(params) + population.arrays()


def _joined(population):
    return population if population is not None and population.joined else None


def select(queryset, fields, population=None, rid='id', overrides=None):
    """SQL and params returning one column per name in ``fields`` (the engine's base query). In view
    mode (``population``) restricted to the view's registrations; ``rid``: the path to the registration
    id (``'registration_id'`` for a service record)."""
    population = _joined(population)
    sql, params = _annotate(queryset, fields, rid if population else None).query.sql_with_params()
    return _renamed(sql, params, fields, population, overrides)


def select_union(querysets, fields_list, population=None, rid='id', overrides=None):
    """The same columns from several querysets, one after the other (UNION ALL). In view mode each queryset
    is also restricted to the view's registrations by itself: PostgreSQL does not push the join with the
    population (outside the UNION ALL) into its branches, so each branch would read its whole table, every
    year's records, and the union of them all would be sorted before the join. The ids stay one bound
    parameter (the population's array), never in the statement text."""
    population = _joined(population)
    if population is not None:
        ids = RawSQL('SELECT unnest(%s::int[])', [population.arrays()[0]])
        querysets = [q.filter(**{rid + '__in': ids}) for q in querysets]
    first, *rest = [_annotate(q, f, rid if population else None) for q, f in zip(querysets, fields_list)]
    sql, params = first.union(*rest, all=True).query.sql_with_params()
    return _renamed(sql, params, fields_list[0], population, overrides)


def view_population(programme, period, **kwargs):
    """power_bi.population(), never failing the count: an unexpected error gives rule mode."""
    try:
        return power_bi.population(programme, period, **kwargs)
    except engine.INTERRUPTS:  # the worker's time limit stops the whole count
        raise
    except Exception as exc:  # recorded in the payload; the count goes on with the rule
        logger.error('figures %s %s: the view population failed: %s', programme, period, power_bi.error_line(exc))
        chosen = power_bi.options(programme)
        return power_bi.Population(view=power_bi.SOURCES[programme].view, deleted=chosen['deleted'],
                                   setting=chosen['base'], reason=power_bi.error_text('population', exc),
                                   errors=[power_bi.error_text('population', exc)])


def power_bi_block(programme, period, population, before, counted, **kwargs):
    try:
        return power_bi.block(programme, period, population, before, counted, **kwargs)
    except engine.INTERRUPTS:
        raise
    except Exception as exc:  # the counts are still sent
        logger.error('figures %s %s: the power_bi block failed: %s', programme, period, power_bi.error_line(exc))
        return power_bi.failed_block(programme, period, exc, kwargs.get('period_rule', ''))


def block(name, sql_params, dimensions, grouping_list, measures=engine.PEOPLE):
    sql, params = sql_params
    try:
        return engine.figures_block(sql, params, dimensions, grouping_list, measures)
    except engine.INTERRUPTS:  # the worker's time limit is not one block's failure: the count stops
        raise
    except Exception as exc:  # one block's failure (e.g. a timeout) leaves the others
        logger.error('figures block %s failed: %s', name, power_bi.error_line(exc))  # never exc_info: SPEC §7
        return {'measures': [m for m, _sql in measures], 'figures': [], 'error': type(exc).__name__}


def cube(name, sql_params, dimensions, measures):
    sql, params = sql_params
    try:
        return engine.cube(sql, params, dimensions, measures)
    except engine.INTERRUPTS:  # the worker's time limit is not one cube's failure: the count stops
        raise
    except Exception as exc:  # one cube's failure (e.g. a timeout) leaves the others
        logger.error('figures cube %s failed: %s', name, power_bi.error_line(exc))  # never exc_info: SPEC §7
        return {'dims': list(dimensions), 'measures': [m for m, _sql in measures], 'rows': [],
                'error': type(exc).__name__}


def ids_in(blocks, dimension):
    """Every value of ``dimension`` found in the single-dimension groupings of ``blocks``."""
    found = set()
    for data in blocks.values():
        for grouping in data.get('figures', []):
            if grouping['by'] == [dimension]:
                found.update(row[0] for row in grouping['rows'] if row[0] is not None)
    return found


def ids_in_cubes(cubes, dimension):
    """Every value of ``dimension`` found in the rows of ``cubes``."""
    found = set()
    for data in cubes.values():
        if dimension in data['dims']:
            position = data['dims'].index(dimension)
            found.update(row[position] for row in data['rows'] if row[position] is not None)
    return found


def yes_no_label(value):
    return {'yes': 'Yes', 'no': 'No'}.get((value or '').strip().lower(), NOT_SPECIFIED)


def coordinates(latitude, longitude):
    """The GPS point as floats, or (None, None) when it is missing, 0 or outside Lebanon."""
    (south, north), (west, east) = LEBANON
    if latitude is None or longitude is None:
        return None, None
    if not (south <= latitude <= north and west <= longitude <= east):
        return None, None
    return float(latitude), float(longitude)


def partners(ids):
    from student_registration.schools.models import PartnerOrganization

    return list(PartnerOrganization.objects.filter(id__in=ids).values('id', 'name', 'short_name'))


def locations(ids):
    from student_registration.locations.models import Location

    return [
        {'id': loc.id, 'name': loc.name_en or loc.name, 'p_code': loc.p_code, 'parent': loc.parent_id,
         'type': loc.type.name if loc.type_id else None}
        for loc in Location.objects.filter(id__in=ids).select_related('type')
    ]


def named(model, ids):
    return [{'id': o.id, 'name': getattr(o, 'name_en', None) or o.name} for o in model.objects.filter(id__in=ids)]


# ------------------------------------------------------------------------------------ Makani
class Makani:
    name = 'mscc'
    label = 'Makani (MSCC)'
    format_version = FORMAT_VERSION

    MAIN = ('partner', 'governorate')
    DETAILS = ('district', 'cadaster', 'center', 'round', 'registration_type', 'sex', 'age_group',
               'nationality', 'disability', 'source', 'center_type')
    EXTRA = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
             ('disability', 'sex'), ('nationality', 'sex'), ('district', 'sex'))
    SUBGROUPS = ('partner', 'governorate', 'sex', 'age_group')
    ENROLMENT = ('center', 'partner', 'governorate', 'sex', 'nationality', 'disability', 'caregiver', 'working',
                 'programme', 'education_status', 'package', 'id_type', 'malnutrition', 'delay')
    ENROLMENT_MEASURES = (
        ('registrations', 'COUNT(*)'),
        ('married', 'SUM(b.married)'),
        ('idp', 'SUM(b.idp)'),
        ('counselling', 'SUM(b.counselling)'),
        ('immunized', 'SUM(b.immunized)'),
        ('screened', 'COUNT(b.malnutrition)'),  # a malnutrition result recorded
        ('minimum_meals', 'SUM(b.minimum_meals)'),
        ('vaccinated', 'SUM(b.vaccinated)'),
        # the variants of two cards whose Power BI measure is unknown (one field or the other)
        ('immunized_record', 'SUM(COALESCE(b.health_bits, 0) & 1)'),
        ('immunized_child', 'SUM((COALESCE(b.health_bits, 0) & 2) / 2)'),
        ('screened_muac', 'SUM((COALESCE(b.health_bits, 0) & 4) / 4)'),
    )
    VIEW_ROWS = (('view_rows', 'SUM(b.view_rows)'),)  # view mode only
    STAFF = ('center', 'partner', 'governorate', 'sex', 'active')

    @staticmethod
    def _rounds():
        from student_registration.mscc.models import Round

        return Round.objects.exclude(year=None)

    def years(self, alias=None):
        rounds = self._rounds().using(alias) if alias else self._rounds()
        return [str(y) for y in sorted(set(rounds.values_list('year', flat=True)), reverse=True)]

    def current_year(self, alias=None):
        """The year of the rounds flagged current, else the latest; ``alias``: the figures connection, when
        read in a count (under the counting limits)."""
        rounds = self._rounds().using(alias) if alias else self._rounds()
        years = list(rounds.filter(current_year=True).values_list('year', flat=True))
        years = years or [int(y) for y in self.years(alias)]
        return str(max(years)) if years else None

    def has_year(self, year):
        return str(year) in self.years()

    def _period_rounds(self, year, period_rule):
        """The rounds of ``year``: rounds whose year is Y ('round_year'), or the rounds flagged current
        ('current_rounds', the current year only). Read under the counting limits."""
        from student_registration.mscc.models import Round

        with engine.read_only_transaction() as alias:
            if period_rule == 'current_rounds':
                rounds = Round.objects.using(alias).filter(current_year=True)
            else:
                rounds = self._rounds().using(alias).filter(year=int(year))
            return list(rounds.order_by('start_date', 'name'))

    @staticmethod
    def _rule(round_ids, prefix=''):
        """Compiler's own rule (rule mode), corrected to what Power BI's view holds: registrations not
        deleted, with a child, in a round of the period, TLS left out (TLS has its own views); no
        registration without a round (``prefix``: the path to Registration from another model)."""
        return (Q(**{prefix + 'deleted': False, prefix + 'child__isnull': False, prefix + 'round__in': round_ids})
                & (~Q(**{prefix + 'type': 'TLS'}) | Q(**{prefix + 'type__isnull': True})))

    def _valid(self, population, round_ids, prefix=''):
        """Registrations counted in the period. View mode: the view's (the population joins them in),
        deleted ones left out unless the setting keeps them; rule mode: ``_rule``."""
        if population.joined:
            return Q(**{prefix + 'deleted': False}) if population.deleted == 'exclude' else Q()
        return self._rule(round_ids, prefix)

    @staticmethod
    def _before(year, current):
        """The rule used before the Power BI alignment (for the reconciliation only): TLS counted, and in
        the current year (``current``) the registrations without a round too."""
        condition = Q(round__year=int(year))
        if current:
            condition |= Q(round__isnull=True)
        return Q(deleted=False, child__isnull=False) & condition

    @staticmethod
    def _pending_round(partner_ids):
        """Registrations waiting for a round (in neither dashboard): not deleted, with a child, not TLS,
        of the partners counted in the current year."""
        from student_registration.mscc.models import Registration

        if not partner_ids:
            return 0
        with engine.read_only_transaction() as alias:
            return (Registration.objects.using(alias)
                    .filter(deleted=False, round__isnull=True, child__isnull=False)
                    .filter(~Q(type='TLS') | Q(type__isnull=True))
                    .annotate(x_owner=Coalesce('partner_id', 'center__partner_id'))
                    .filter(x_owner__in=list(partner_ids)).count())

    def _child(self, year, prefix=''):
        """The columns every child block shares: the child, partner, place, sex and age group."""
        born, age = age_group(prefix + 'child__birthday_year', int(year))
        return {
            'person': F(prefix + 'child_id'),
            'partner': Coalesce(prefix + 'partner_id', prefix + 'center__partner_id'),
            'governorate': F(prefix + 'center__governorate_id'),
            'district': F(prefix + 'center__caza_id'),
            'sex': sex(prefix + 'child__gender'),
            '_born': born,
            'age_group': age,
        }

    @staticmethod
    def _enrolment():
        """One row per registration: the slicers of the dashboard and the flags its cards add up.
        The education programme and status, and the health and nutrition answers, are those of the
        registration's latest record."""
        from student_registration.mscc.models import EducationService
        from student_registration.mscc.models import HealthNutritionService as Health

        def yes(field):
            return Q(**{field + '__iexact': 'yes'})

        return {
            'center': F('center_id'),
            'partner': Coalesce('partner_id', 'center__partner_id'),
            'governorate': F('center__governorate_id'),
            'sex': sex('child__gender'),
            'nationality': F('child__nationality_id'),
            'disability': F('child__disability_id'),
            'caregiver': caregiver('child__main_caregiver'),
            'working': Case(When(have_labour__istartswith='yes', then=Value('Yes')),
                            When(have_labour__iexact='no', then=Value('No')),
                            default=Value(NOT_SPECIFIED), output_field=CharField()),
            'programme': blank_to_null(latest(EducationService, 'education_program')),
            'education_status': blank_to_null(latest(EducationService, 'education_status')),
            'package': blank_to_null(F('type')),
            'id_type': F('child__id_type_id'),
            'malnutrition': latest(Health, Coalesce(blank_to_null(F('muac_malnutrition_screening')),
                                                    blank_to_null(F('child_malnutrition_screening')))),
            'delay': blank_to_null(latest(Health, 'development_delays_identified')),
            'married': _flag(Q(child__marital_status__iexact='married')),
            'idp': _flag(yes('child_is_idp')),
            'counselling': _flag(Exists(Health.objects.filter(yes('caregiver_counselling'),
                                                              registration=OuterRef('pk')))),
            'immunized': Coalesce(latest(Health, _flag(yes('immunization_record_screened')
                                                       | yes('child_immunization_screened'))), Value(0)),
            'minimum_meals': Coalesce(latest(Health, _flag(yes('eating_minimum_meals'))), Value(0)),
            'vaccinated': Coalesce(latest(Health, _flag(yes('child_vaccinated'))), Value(0)),
            # the latest record's immunization record (1), child immunization (2), MUAC result (4)
            'health_bits': latest(Health, _flag(yes('immunization_record_screened'))
                                  + _flag(yes('child_immunization_screened')) * Value(2)
                                  + _flag(~Q(muac_malnutrition_screening='')
                                          & Q(muac_malnutrition_screening__isnull=False)) * Value(4)),
        }

    @staticmethod
    def _centers(ids):
        from student_registration.locations.models import Center

        out = []
        for c in Center.objects.filter(id__in=ids).order_by('id'):
            latitude, longitude = coordinates(c.latitude, c.longitude)
            out.append({'id': c.id, 'name': c.name, 'partner': c.partner_id, 'governorate': c.governorate_id,
                        'district': c.caza_id, 'cadaster': c.cadaster_id, 'type': c.type or None,
                        'emergency': yes_no_label(c.active_during_emergency), 'is_active': c.is_active,
                        'latitude': latitude, 'longitude': longitude})
        return out

    def build(self, year):
        from student_registration.attendances.models import MSCCAttendanceChild
        from student_registration.clm.models import Disability
        from student_registration.locations.models import Center, ProgramStaff
        from student_registration.mscc import models as m
        from student_registration.students.models import IDType, Nationality

        year = str(year)
        with engine.read_only_transaction() as alias:  # every read of a count under the limits
            current = year == self.current_year(alias)
        chosen = power_bi.options(self.name)
        period_rule = chosen['period'] if current else 'round_year'
        rounds = self._period_rounds(year, period_rule)
        round_ids = [r.id for r in rounds] or [0]
        population = view_population(self.name, year, round_ids=round_ids,
                                     rule=m.Registration.objects.filter(self._rule(round_ids)))
        registrations = m.Registration.objects.filter(self._valid(population, round_ids))
        fields = dict(
            self._child(year),
            cadaster=F('center__cadaster_id'),
            center=F('center_id'),
            round=F('round_id'),
            registration_type=Coalesce('type', Value(NOT_SPECIFIED)),
            nationality=F('child__nationality_id'),
            disability=F('child__disability_id'),
            source=Coalesce('source_of_identification', Value(NOT_SPECIFIED)),
            center_type=F('center__type'),
        )
        blocks = {'registrations': block(
            'registrations', select(registrations, fields, population),
            self.MAIN + self.DETAILS, engine.groupings(self.MAIN, self.DETAILS, self.EXTRA))}

        # services: one row per service record (a child counts once per service)
        services = (
            ('Education', m.EducationService), ('Child protection (PSS)', m.PSSService),
            ('Health and nutrition', m.HealthNutritionService), ('Digital learning', m.DigitalService),
            ('Youth', m.YouthService), ('Youth kit', m.YouthKitService), ('Follow-up', m.FollowUpService),
            ('Inclusion', m.InclusionService), ('Recreational', m.Recreational), ('Lego', m.LegoService),
            ('Referral', m.Referral),
        )
        querysets, fields_list = [], []
        for label, model in services:
            querysets.append(model.objects.filter(self._valid(population, round_ids, 'registration__')))
            fields_list.append(dict(self._child(year, 'registration__'),
                                    service=Value(label, output_field=CharField())))
        blocks['services'] = block(
            'services', select_union(querysets, fields_list, population, rid='registration_id'),
            ('service',) + self.SUBGROUPS,
            engine.groupings(('service', 'partner', 'governorate'), ('sex', 'age_group')))

        fields = dict(self._child(year, 'registration__'),
                      education_programme=Coalesce('education_program', Value(NOT_SPECIFIED)))
        blocks['education_programmes'] = block(
            'education_programmes',
            select(m.EducationService.objects.filter(self._valid(population, round_ids, 'registration__')), fields,
                   population, rid='registration_id'),
            ('education_programme',) + self.SUBGROUPS,
            engine.groupings(('education_programme', 'partner', 'governorate'), ('sex', 'age_group')))

        # sites: centers with at least one child registered in the year
        fields = {
            'person': F('center_id'),
            'partner': Coalesce('partner_id', 'center__partner_id'),
            'governorate': F('center__governorate_id'),
            'district': F('center__caza_id'),
            'site_type': Coalesce('center__type', Value(NOT_SPECIFIED)),
        }
        blocks['sites'] = block(
            'sites', select(registrations.filter(center__isnull=False), fields, population,
                            overrides={'person': 'center'}),
            ('partner', 'governorate', 'district', 'site_type'),
            engine.groupings(('partner', 'governorate'), ('district', 'site_type')))

        # staff: the centers' facilitators (the record has no year: today's list)
        fields = {
            'person': F('id'),
            'partner': F('center__partner_id'),
            'governorate': F('center__governorate_id'),
            'sex': sex('gender'),
            'active': yes_no('is_active_current_round'),  # a choice: free text never sent
        }
        blocks['staff'] = block(
            'staff', select(ProgramStaff.objects.filter(center__isnull=False), fields),
            ('partner', 'governorate', 'sex', 'active'),
            engine.groupings(('partner', 'governorate'), ('sex', 'active')))

        # attendance: days recorded and attended, days off left out
        attendance = MSCCAttendanceChild.objects.filter(
            attendance_day__round_id__in=[r.id for r in rounds] or [0],
        ).exclude(attendance_day__day_off__iexact='yes')
        fields = {
            'person': F('child_id'),
            'partner': Coalesce('registration__partner_id', 'attendance_day__center__partner_id'),
            'governorate': F('attendance_day__center__governorate_id'),
            'month': month_of('attendance_day__attendance_date'),
            'education_programme': Coalesce('attendance_day__education_program', Value(NOT_SPECIFIED)),
            'present': PRESENT,
        }
        blocks['attendance'] = block(
            'attendance', select(attendance, fields), ('partner', 'governorate', 'month', 'education_programme'),
            engine.groupings(('partner', 'governorate'), ('month', 'education_programme')), ATTENDANCE)

        # cubes: registrations, and today's facilitators, per combination of the dashboard's slicers
        measures = self.ENROLMENT_MEASURES + (self.VIEW_ROWS if population.joined else ())
        cubes = {
            'enrolment': cube('enrolment', select(registrations, self._enrolment(), population),
                              self.ENROLMENT, measures),
            'staff': cube('staff', select(ProgramStaff.objects.filter(center__isnull=False), {
                'center': F('center_id'),
                'partner': F('center__partner_id'),
                'governorate': F('center__governorate_id'),
                'sex': sex('gender'),
                'active': yes_no('is_active_current_round'),
            }), self.STAFF, (('staff', 'COUNT(*)'),)),
        }
        centers_seen = self._centers(ids_in_cubes(cubes, 'center'))
        places = {c[k] for c in centers_seen for k in ('governorate', 'district', 'cadaster') if c[k]}

        pending_round = 0
        if current:
            try:
                pending_round = self._pending_round(
                    ids_in_cubes({'enrolment': cubes['enrolment']}, 'partner')
                    | ids_in({'registrations': blocks['registrations']}, 'partner'))
            except engine.INTERRUPTS:
                raise
            except Exception as exc:  # recorded in power_bi.errors
                logger.error('figures mscc %s: pending_round failed: %s', year, power_bi.error_line(exc))
                population.errors.append(power_bi.error_text('pending_round', exc))
        power = power_bi_block(self.name, year, population,
                               m.Registration.objects.filter(self._before(year, current)),
                               registrations, current=current, period_rule=period_rule)

        centers = Center.objects.filter(id__in=ids_in(blocks, 'center'))
        return {
            'format': FORMAT_VERSION,
            'programme': self.name,
            'label': self.label,
            'year': year,
            'generated_at': timezone.now().isoformat(),
            'counts': COUNTS,
            'rounds': [{'id': r.id, 'name': r.name, 'start_date': _iso(r.start_date),
                        'end_date': _iso(r.end_date), 'current': r.current_year} for r in rounds],
            'partners': partners(ids_in(blocks, 'partner') | ids_in_cubes(cubes, 'partner')
                                 | {c['partner'] for c in centers_seen if c['partner']}),
            'locations': locations(ids_in(blocks, 'governorate') | ids_in(blocks, 'district')
                                   | ids_in(blocks, 'cadaster') | ids_in_cubes(cubes, 'governorate') | places),
            'sites': [{'id': c.id, 'name': c.name, 'partner': c.partner_id, 'governorate': c.governorate_id,
                       'district': c.caza_id, 'type': c.type} for c in centers],
            'centers': centers_seen,
            'nationalities': named(Nationality, ids_in(blocks, 'nationality') | ids_in_cubes(cubes, 'nationality')),
            'disabilities': named(Disability, ids_in(blocks, 'disability') | ids_in_cubes(cubes, 'disability')),
            'id_types': named(IDType, ids_in_cubes(cubes, 'id_type')),
            'blocks': blocks,
            'cubes': cubes,
            'pending_round': pending_round,
            'power_bi': power,
        }


# ---------------------------------------------------------------------------------- Bridging
class Bridging:
    name = 'bridging'
    label = 'Bridging (Dirasa)'
    format_version = FORMAT_VERSION

    MAIN = ('partner', 'governorate')
    DETAILS = ('district', 'cadaster', 'school', 'registration_level', 'sex', 'age_group', 'nationality',
               'disability', 'learning_result', 'education_status', 'source', 'round')
    EXTRA = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
             ('registration_level', 'sex'), ('disability', 'sex'), ('nationality', 'sex'),
             ('learning_result', 'sex'), ('district', 'sex'), ('round', 'sex'))
    SUBGROUPS = ('partner', 'governorate', 'sex', 'age_group')
    SERVICES = (
        ('Social assistance', 'receiving_social_assistance'),
        ('Transportation support', 'receiving_transportation_support'),
        ('Basic stationery', 'basic_stationery'),
        ('Internet', 'child_received_internet'),
        ('PSS session', 'pss_session_attended'),
        ('Child protection referral', 'cp_referral'),
        ('WASH referral', 'referal_wash'),
        ('Health referral', 'referal_health'),
        ('Other referral', 'referal_other'),
    )
    ENROLMENT = ('school', 'partner', 'governorate', 'sex', 'nationality', 'disability', 'level', 'learning_result',
                 'barrier', 'round')
    # the children numbers each school reports (one value per school, no round)
    SCHOOL_COUNTS = (
        ('children', 'number_children'),
        ('children_male', 'number_children_male'),
        ('children_female', 'number_children_female'),
        ('children_lebanese', 'number_children_lebanese'),
        ('children_non_lebanese', 'number_children_non_lebanese'),
        ('cwd', 'number_total_children_disability'),
        ('dirasa_children', 'number_children_sbp'),
        ('dirasa_cwd', 'number_dirasa_children_disability'),
    )

    @staticmethod
    def _bridging_rounds(alias=None):
        """The CLM rounds that are Bridging rounds: a Bridging start date, flagged current for Bridging, or
        with a Bridging registration (deleted or not) or a teacher. ``CLMRound`` is shared by every CLM
        programme: a round of another programme only (a BLN round) makes no Dirasa year. Read in Python (tens
        of rows); ``alias``: the figures connection, when read in a count (under the counting limits)."""
        from student_registration.clm.models import Bridging as Registration
        from student_registration.schools.models import CLMRound
        from student_registration.students.models import Teacher

        rounds = CLMRound.objects.using(alias) if alias else CLMRound.objects.all()
        rounds = rounds.filter(
            Q(start_date_bridging__isnull=False) | Q(current_round_bridging=True)
            | Exists(Registration.objects.filter(round=OuterRef('pk')))
            | Exists(Teacher.objects.filter(round=OuterRef('pk'))))
        return list(rounds.order_by(F('start_date_bridging').desc(nulls_last=True), '-id'))

    def years(self, alias=None):
        """The years of the Bridging rounds (power_bi.bridging_year), as text, the newest first; a round in
        no year adds none."""
        found = {power_bi.bridging_year(r)[0] for r in self._bridging_rounds(alias)}
        return [str(y) for y in sorted(found - {None}, reverse=True)]

    def current_year(self, alias=None):
        """Among the Bridging rounds that have a year: the year of the round flagged current for Bridging
        (the latest-starting one if several), else of the latest-starting round flagged current_year, else
        the newest year; None when there is none. A flagged round in no year is passed over."""
        rounds = [r for r in self._bridging_rounds(alias) if power_bi.bridging_year(r)[0] is not None]
        flagged = ([r for r in rounds if r.current_round_bridging] or [r for r in rounds if r.current_year])
        if flagged:  # latest Bridging start first (nulls last), as _bridging_rounds orders them
            return str(power_bi.bridging_year(flagged[0])[0])
        years = sorted({power_bi.bridging_year(r)[0] for r in rounds}, reverse=True)
        return str(years[0]) if years else None

    def has_year(self, year):
        return str(year).strip() in self.years()

    def _period_rounds(self, year, period_rule):
        """(the rounds of ``year``, the period rule used). 'start_year': the Bridging rounds whose year
        (power_bi.bridging_year) is Y; 'current_rounds' (the current year only): the Bridging rounds flagged
        current_year, as Compiler's own Bridging list, and when none is, the 'start_year' rounds (reported as
        'start_year'). Ordered by Bridging start (nulls last), then name. Read under the counting limits."""
        number = int(year) if str(year).strip().isdigit() else None
        with engine.read_only_transaction() as alias:
            rounds = self._bridging_rounds(alias)
        chosen = [r for r in rounds if r.current_year] if period_rule == 'current_rounds' else []
        if not chosen:
            period_rule = 'start_year'
            chosen = [r for r in rounds if number is not None and power_bi.bridging_year(r)[0] == number]
        return sorted(chosen, key=lambda r: (r.start_date_bridging is None, r.start_date_bridging or datetime.date.min,
                                             r.name)), period_rule

    @staticmethod
    def _child(reference_year):
        born, age = age_group('student__birthday_year', reference_year)
        return {
            'person': F('student_id'),
            'partner': F('partner_id'),
            'governorate': F('governorate_id'),
            'district': F('district_id'),
            'sex': sex('student__sex'),
            '_born': born,
            'age_group': age,
        }

    def _schools(self, cubes):
        """The schools of the cubes. A school's partners are those that registered children there in
        the year, else the Dirasa partners that list it."""
        from student_registration.schools.models import PartnerOrganization, School

        ids = ids_in_cubes(cubes, 'school')
        registered, listed = {}, {}
        enrolment = cubes['enrolment']
        school_at, partner_at = enrolment['dims'].index('school'), enrolment['dims'].index('partner')
        for row in enrolment['rows']:
            if row[school_at] is not None and row[partner_at] is not None:
                registered.setdefault(row[school_at], set()).add(row[partner_at])
        links = PartnerOrganization.schools.through.objects.filter(
            school_id__in=ids, partnerorganization__is_dirasa=True).values_list('school_id', 'partnerorganization_id')
        for school_id, partner_id in links:
            listed.setdefault(school_id, set()).add(partner_id)
        counts = [field for _name, field in self.SCHOOL_COUNTS]
        out = []
        for school in School.objects.filter(id__in=ids).order_by('id').values(
                'id', 'name', 'number', 'type', 'governorate_id', 'district_id', 'active_during_emergency',
                'latitude', 'longitude', *counts):
            latitude, longitude = coordinates(school['latitude'], school['longitude'])
            out.append({
                'id': school['id'], 'name': school['name'], 'number': school['number'],
                'type': school['type'] or None, 'governorate': school['governorate_id'],
                'district': school['district_id'], 'emergency': yes_no_label(school['active_during_emergency']),
                'latitude': latitude, 'longitude': longitude,
                'partners': sorted(registered.get(school['id']) or listed.get(school['id']) or ()),
                'counts': {name: school[field] for name, field in self.SCHOOL_COUNTS},
            })
        return out

    def build(self, year):
        from student_registration.attendances.models import CLMAttendanceStudent
        from student_registration.clm.models import Bridging as Registration
        from student_registration.clm.models import Disability
        from student_registration.schools.models import School
        from student_registration.students.models import Nationality, Teacher, Training

        year = str(year).strip()
        with engine.read_only_transaction() as alias:  # every read of a count under the limits
            current = year == self.current_year(alias)
        chosen = power_bi.options(self.name)
        period_rule = chosen['period'] if current else 'start_year'  # a past year: always the rounds of its year
        rounds, period_rule = self._period_rounds(year, period_rule)
        round_ids = [r.id for r in rounds] or [0]
        # ages in the year itself (a round without a year cannot be asked for: has_year)
        reference_year = int(year) if year.isdigit() else timezone.localdate().year
        rule = Registration.objects.filter(deleted=False, round__in=round_ids, student__isnull=False)
        population = view_population(self.name, year, round_ids=round_ids, rule=rule)
        if not population.joined:
            valid = rule
        elif population.deleted == 'exclude':  # the view's registrations (the population joins them in)
            valid = Registration.objects.filter(deleted=False)
        else:
            valid = Registration.objects.all()
        fields = dict(
            self._child(reference_year),
            cadaster=F('cadaster_id'),
            school=F('school_id'),
            registration_level=Coalesce('registration_level', Value(NOT_SPECIFIED)),
            nationality=F('student__nationality_id'),
            disability=F('disability_id'),
            learning_result=Coalesce('learning_result', Value('in_progress')),
            education_status=Coalesce('education_status', Value(NOT_SPECIFIED)),
            source=Coalesce('source_of_identification', Value(NOT_SPECIFIED)),
            round=F('round_id'),
            pre_tested=_flag(~Q(pre_test={}) & Q(pre_test__isnull=False)),
            post_tested=_flag(~Q(post_test={}) & Q(post_test__isnull=False)),
        )
        enrolment = {
            'school': F('school_id'),
            'partner': F('partner_id'),
            'governorate': F('governorate_id'),  # the child's governorate
            'sex': sex('student__sex'),
            'nationality': F('student__nationality_id'),
            'disability': F('disability_id'),
            'level': blank_to_null(F('registration_level')),
            'learning_result': Coalesce(blank_to_null(F('learning_result')), Value('in_progress')),
            'barrier': blank_to_null(F('barriers_single')),
            'round': F('round_id'),  # the registration's round (in view mode too)
            'pre_tested': fields['pre_tested'],
            'post_tested': fields['post_tested'],
        }
        measures = engine.PEOPLE + (
            ('pre_tested', 'COUNT(DISTINCT b.person) FILTER (WHERE b.pre_tested = 1)'),
            ('post_tested', 'COUNT(DISTINCT b.person) FILTER (WHERE b.post_tested = 1)'),
        )
        blocks = {'registrations': block(
            'registrations', select(valid, fields, population), self.MAIN + self.DETAILS,
            engine.groupings(self.MAIN, self.DETAILS, self.EXTRA), measures)}

        querysets, fields_list = [], []
        services = [(label, Q(**{field + '__iexact': 'yes'})) for label, field in self.SERVICES]
        services.append(('Digital platform', Q(using_digital_platform__istartswith='yes')))
        for label, condition in services:
            querysets.append(valid.filter(condition))
            fields_list.append(dict(self._child(reference_year), service=Value(label, output_field=CharField())))
        blocks['services'] = block(
            'services', select_union(querysets, fields_list, population), ('service',) + self.SUBGROUPS,
            engine.groupings(('service', 'partner', 'governorate'), ('sex', 'age_group')))

        fields = {
            'person': F('school_id'),
            'partner': F('partner_id'),
            'governorate': F('governorate_id'),
            'district': F('district_id'),
            'site_type': Coalesce('school__type', Value(NOT_SPECIFIED)),
        }
        blocks['sites'] = block(
            'sites', select(valid.filter(school__isnull=False), fields, population, overrides={'person': 'school'}),
            ('partner', 'governorate', 'district', 'site_type'),
            engine.groupings(('partner', 'governorate'), ('district', 'site_type')))

        # teachers of the year's rounds (one record per teacher and round, as stored); a school's partners are
        # the partners that list it
        fields = {
            'person': F('id'),
            'partner': F('school__partner_schools__id'),
            'governorate': F('school__governorate_id'),
            'sex': sex('sex'),
            'assignment': Coalesce('teacher_assignment', Value(NOT_SPECIFIED)),
            'active': yes_no('is_active_current_round'),  # a choice: free text never sent
        }
        blocks['staff'] = block(
            'staff', select(Teacher.objects.filter(round__in=round_ids), fields),
            ('partner', 'governorate', 'sex', 'assignment', 'active'),
            engine.groupings(('partner', 'governorate'), ('sex', 'assignment', 'active')))

        attendance = CLMAttendanceStudent.objects.filter(
            attendance_day__round_id__in=round_ids,
        ).exclude(attendance_day__day_off__iexact='yes')
        fields = {
            'person': F('student_id'),
            'partner': F('registration__partner_id'),
            'governorate': F('registration__governorate_id'),
            'month': month_of('attendance_day__attendance_date'),
            'registration_level': Coalesce('attendance_day__registration_level', Value(NOT_SPECIFIED)),
            'present': PRESENT,
        }
        blocks['attendance'] = block(
            'attendance', select(attendance, fields), ('partner', 'governorate', 'month', 'registration_level'),
            engine.groupings(('partner', 'governorate'), ('month', 'registration_level')), ATTENDANCE)

        # cubes: registrations, teachers, and teachers per training topic, per combination of slicers
        teachers = Teacher.objects.filter(round__in=round_ids)
        trained = Teacher.trainings.through.objects.filter(teacher__round__in=round_ids)
        cubes = {
            'enrolment': cube('enrolment', select(valid, enrolment, population), self.ENROLMENT, (
                ('registrations', 'COUNT(*)'), ('pre_tested', 'SUM(b.pre_tested)'),
                ('post_tested', 'SUM(b.post_tested)')) + (Makani.VIEW_ROWS if population.joined else ())),
            'teachers': cube('teachers', select(teachers, {
                'school': F('school_id'),
                'sex': sex('sex'),
                'round': F('round_id'),
            }), ('school', 'sex', 'round'), (('teachers', 'COUNT(*)'),)),
            'trainings': cube('trainings', select(trained, {
                'school': F('teacher__school_id'),
                'sex': sex('teacher__sex'),
                'training': F('training_id'),
                'round': F('teacher__round_id'),
            }), ('school', 'sex', 'training', 'round'), (('teachers', 'COUNT(*)'),)),
        }
        schools_seen = self._schools(cubes)
        places = {s[k] for s in schools_seen for k in ('governorate', 'district') if s[k]}
        try:
            school_totals = self._school_totals()
        except engine.INTERRUPTS:
            raise
        except Exception as exc:  # recorded in power_bi.errors
            logger.error('figures bridging %s: school_totals failed: %s', year, power_bi.error_line(exc))
            population.errors.append(power_bi.error_text('school_totals', exc))
            school_totals = {}
        power = power_bi_block(self.name, year, population, rule, valid, current=current, period_rule=period_rule)

        schools = School.objects.filter(id__in=ids_in(blocks, 'school'))
        return {
            'format': FORMAT_VERSION,
            'programme': self.name,
            'label': self.label,
            'year': year,
            'generated_at': timezone.now().isoformat(),
            'counts': COUNTS,
            'rounds': [self._round_entry(r) for r in rounds],
            'partners': partners(ids_in(blocks, 'partner') | ids_in_cubes(cubes, 'partner')
                                 | {p for s in schools_seen for p in s['partners']}),
            'locations': locations(ids_in(blocks, 'governorate') | ids_in(blocks, 'district')
                                   | ids_in(blocks, 'cadaster') | ids_in_cubes(cubes, 'governorate') | places),
            'sites': [{'id': s.id, 'name': s.name, 'number': s.number, 'governorate': s.governorate_id,
                       'district': s.district_id, 'type': s.type} for s in schools],
            'schools': schools_seen,
            'nationalities': named(Nationality, ids_in(blocks, 'nationality') | ids_in_cubes(cubes, 'nationality')),
            'disabilities': named(Disability, ids_in(blocks, 'disability') | ids_in_cubes(cubes, 'disability')),
            'trainings': [{'id': t.id, 'name': t.name} for t in Training.objects.order_by('name', 'id')],
            'blocks': blocks,
            'cubes': cubes,
            'outreach': outreach(),
            'school_totals': school_totals,
            'power_bi': power,
        }

    @staticmethod
    def _round_entry(the_round):
        """A round of the year in the payload: its own year and where it comes from (under
        ``current_rounds`` a round flagged current may start in another year)."""
        year, year_from = power_bi.bridging_year(the_round)
        return {'id': the_round.id, 'name': the_round.name, 'start_date': _iso(the_round.start_date_bridging),
                'end_date': _iso(the_round.end_date_bridging), 'current': the_round.current_round_bridging,
                'current_year': the_round.current_year, 'year': year, 'year_from': year_from}

    def _school_totals(self):
        """The school-reported numbers summed over every school a Dirasa partner lists (``listed``) and
        over every school (``all``), a blank counting 0: candidates of the In-school and CWD cards."""
        from django.db.models import Count, Sum

        from student_registration.schools.models import PartnerOrganization, School

        sums = {name: Coalesce(Sum(field), 0) for name, field in self.SCHOOL_COUNTS}
        listed = PartnerOrganization.schools.through.objects.filter(
            partnerorganization__is_dirasa=True).values('school_id')
        with engine.read_only_transaction() as alias:
            schools = School.objects.using(alias)
            return {'listed': schools.filter(id__in=listed).aggregate(schools=Count('id'), **sums),
                    'all': schools.aggregate(schools=Count('id'), **sums)}


# ---------------------------------------------------------------------------------- outreach
OUTREACH = ('year', 'partner', 'governorate', 'value')
OUTREACH_QUESTIONS = (
    ('education_status', 'education_status'),
    ('referral', 'child_referral'),
    ('dropout_reason', 'dropout_reason'),
    ('id_type', 'outreach_caregiver__id_type'),
)


def outreach():
    """The Kobo outreach children (shared by all programmes, every year) per year of the interview,
    partner, governorate and answer. Partner and governorate are the Kobo form's own text."""
    from student_registration.outreach.models import OutreachChild

    date = 'outreach_caregiver__interview_date'
    common = {
        'year': Case(When(**{date + '__regex': r'^[0-9]{4}'}, then=Left(date, 4)), default=None,
                     output_field=CharField()),
        'partner': blank_to_null(Trim('outreach_caregiver__partner_name')),
        'governorate': blank_to_null(Trim('outreach_caregiver__governorate')),
    }
    return {'cubes': {
        name: cube('outreach ' + name, select(OutreachChild.objects.all(), dict(common, value=text_key(path))),
                   OUTREACH, (('children', 'COUNT(*)'),))
        for name, path in OUTREACH_QUESTIONS
    }}


COUNTS = 'unique children per grouping (attendance: days), no personal data'
PRESENT = Case(When(attended__iexact='yes', then=Value(1)), default=Value(0), output_field=IntegerField())
ATTENDANCE = (('days_recorded', 'COUNT(*)'), ('days_attended', 'SUM(b.present)'))


def _flag(condition):
    return Case(When(condition, then=Value(1)), default=Value(0), output_field=IntegerField())


def _iso(value):
    return value.isoformat() if isinstance(value, (datetime.date, datetime.datetime)) else None


PROGRAMMES = {p.name: p for p in (Makani(), Bridging())}
