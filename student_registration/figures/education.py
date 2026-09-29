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

Which registrations count follows the partners' own lists: Makani, registrations not deleted in the
rounds of the year (the current year also counts registrations without a round yet); Bridging,
registrations not deleted in the round. A child who dropped out still counts as reached; the
learning result shows the dropouts. A child is counted once per figure, however many services,
records or partners.
"""

from __future__ import annotations

import datetime
import logging

from django.db.models import (
    Case,
    CharField,
    F,
    Func,
    IntegerField,
    Q,
    Value,
    When,
)
from django.db.models.functions import Cast, Coalesce
from django.utils import timezone

from . import engine

logger = logging.getLogger(__name__)

FORMAT_VERSION = 1
NOT_SPECIFIED = 'Not specified'
AGE_GROUPS = ('Under 6', '6-9', '10-14', '15-17', '18 and over', NOT_SPECIFIED)


# ---------------------------------------------------------------------------------------- helpers
def sex(path):
    return Case(
        When(**{path: 'Male'}, then=Value('Male')),
        When(**{path: 'Female'}, then=Value('Female')),
        default=Value(NOT_SPECIFIED),
        output_field=CharField(),
    )


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


def _annotate(queryset, fields):
    """Annotate ``fields`` (name -> expression) under prefixed names: an annotation may not share a
    model field's name. Names starting with "_" are helpers (kept as they are, not selected)."""
    for name, expression in fields.items():
        queryset = queryset.annotate(**{(name if name.startswith('_') else 'x_' + name): expression})
    return queryset.order_by().values(*['x_' + n for n in fields if not n.startswith('_')])


def _renamed(sql, fields):
    names = [n for n in fields if not n.startswith('_')]
    return 'SELECT %s FROM (%s) AS r' % (', '.join('r.x_%s AS %s' % (n, n) for n in names), sql)


def select(queryset, fields):
    """SQL and params returning one column per name in ``fields`` (the engine's base query)."""
    sql, params = _annotate(queryset, fields).query.sql_with_params()
    return _renamed(sql, fields), params


def select_union(querysets, fields_list):
    """The same columns from several querysets, one after the other (UNION ALL)."""
    first, *rest = [_annotate(q, f) for q, f in zip(querysets, fields_list)]
    sql, params = first.union(*rest, all=True).query.sql_with_params()
    return _renamed(sql, fields_list[0]), params


def block(name, sql_params, dimensions, grouping_list, measures=engine.PEOPLE):
    sql, params = sql_params
    try:
        return engine.figures_block(sql, params, dimensions, grouping_list, measures)
    except Exception as exc:  # one block's failure (e.g. a timeout) leaves the others
        logger.exception('figures block %s failed', name)
        return {'measures': [m for m, _sql in measures], 'figures': [], 'error': type(exc).__name__}


def ids_in(blocks, dimension):
    """Every value of ``dimension`` found in the single-dimension groupings of ``blocks``."""
    found = set()
    for data in blocks.values():
        for grouping in data.get('figures', []):
            if grouping['by'] == [dimension]:
                found.update(row[0] for row in grouping['rows'] if row[0] is not None)
    return found


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

    MAIN = ('partner', 'governorate')
    DETAILS = ('district', 'cadaster', 'center', 'round', 'registration_type', 'sex', 'age_group',
               'nationality', 'disability', 'source', 'center_type')
    EXTRA = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
             ('disability', 'sex'), ('nationality', 'sex'), ('district', 'sex'))
    SUBGROUPS = ('partner', 'governorate', 'sex', 'age_group')

    @staticmethod
    def _rounds():
        from student_registration.mscc.models import Round

        return Round.objects.exclude(year=None)

    def years(self):
        return [str(y) for y in sorted(set(self._rounds().values_list('year', flat=True)), reverse=True)]

    def current_year(self):
        years = list(self._rounds().filter(current_year=True).values_list('year', flat=True))
        years = years or [int(y) for y in self.years()]
        return str(max(years)) if years else None

    def has_year(self, year):
        return str(year) in self.years()

    def _valid(self, year, prefix=''):
        """Registrations counted in ``year`` (``prefix``: the path to Registration from another model)."""
        condition = Q(**{prefix + 'round__year': int(year)})
        if str(year) == self.current_year():  # not yet given a round: counted in the current year
            condition |= Q(**{prefix + 'round__isnull': True})
        return Q(**{prefix + 'deleted': False, prefix + 'child__isnull': False}) & condition

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

    def build(self, year):
        from student_registration.attendances.models import MSCCAttendanceChild
        from student_registration.clm.models import Disability
        from student_registration.locations.models import Center, ProgramStaff
        from student_registration.mscc import models as m
        from student_registration.students.models import Nationality

        year = str(year)
        rounds = list(self._rounds().filter(year=int(year)).order_by('start_date', 'name'))
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
            'registrations', select(m.Registration.objects.filter(self._valid(year)), fields),
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
            querysets.append(model.objects.filter(self._valid(year, 'registration__')))
            fields_list.append(dict(self._child(year, 'registration__'),
                                    service=Value(label, output_field=CharField())))
        blocks['services'] = block(
            'services', select_union(querysets, fields_list), ('service',) + self.SUBGROUPS,
            engine.groupings(('service', 'partner', 'governorate'), ('sex', 'age_group')))

        fields = dict(self._child(year, 'registration__'),
                      education_programme=Coalesce('education_program', Value(NOT_SPECIFIED)))
        blocks['education_programmes'] = block(
            'education_programmes',
            select(m.EducationService.objects.filter(self._valid(year, 'registration__')), fields),
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
            'sites', select(m.Registration.objects.filter(self._valid(year), center__isnull=False), fields),
            ('partner', 'governorate', 'district', 'site_type'),
            engine.groupings(('partner', 'governorate'), ('district', 'site_type')))

        # staff: the centers' facilitators (the record has no year: today's list)
        fields = {
            'person': F('id'),
            'partner': F('center__partner_id'),
            'governorate': F('center__governorate_id'),
            'sex': sex('gender'),
            'active': Coalesce('is_active_current_round', Value(NOT_SPECIFIED)),
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
            'partners': partners(ids_in(blocks, 'partner')),
            'locations': locations(ids_in(blocks, 'governorate') | ids_in(blocks, 'district')
                                   | ids_in(blocks, 'cadaster')),
            'sites': [{'id': c.id, 'name': c.name, 'partner': c.partner_id, 'governorate': c.governorate_id,
                       'district': c.caza_id, 'type': c.type} for c in centers],
            'nationalities': named(Nationality, ids_in(blocks, 'nationality')),
            'disabilities': named(Disability, ids_in(blocks, 'disability')),
            'blocks': blocks,
        }


# ---------------------------------------------------------------------------------- Bridging
class Bridging:
    name = 'bridging'
    label = 'Bridging (Dirasa)'

    MAIN = ('partner', 'governorate')
    DETAILS = ('district', 'cadaster', 'school', 'registration_level', 'sex', 'age_group', 'nationality',
               'disability', 'learning_result', 'education_status', 'source')
    EXTRA = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
             ('registration_level', 'sex'), ('disability', 'sex'), ('nationality', 'sex'),
             ('learning_result', 'sex'), ('district', 'sex'))
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

    @staticmethod
    def _rounds():
        from student_registration.schools.models import CLMRound

        return CLMRound.objects.order_by(F('start_date_bridging').desc(nulls_last=True), '-id')

    def years(self):
        return list(self._rounds().values_list('name', flat=True))

    def current_year(self):
        rounds = self._rounds()
        current = rounds.filter(current_round_bridging=True).first() or rounds.filter(current_year=True).first()
        return current.name if current else None

    def has_year(self, year):
        return self._rounds().filter(name=year).exists()

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

    def build(self, year):
        from student_registration.attendances.models import CLMAttendanceStudent
        from student_registration.clm.models import Bridging as Registration
        from student_registration.clm.models import Disability
        from student_registration.schools.models import School
        from student_registration.students.models import Nationality, Teacher

        the_round = self._rounds().get(name=year)
        start = the_round.start_date_bridging
        reference_year = start.year if start else timezone.localdate().year
        valid = Registration.objects.filter(deleted=False, round=the_round, student__isnull=False)
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
            pre_tested=_flag(~Q(pre_test={}) & Q(pre_test__isnull=False)),
            post_tested=_flag(~Q(post_test={}) & Q(post_test__isnull=False)),
        )
        measures = engine.PEOPLE + (
            ('pre_tested', 'COUNT(DISTINCT b.person) FILTER (WHERE b.pre_tested = 1)'),
            ('post_tested', 'COUNT(DISTINCT b.person) FILTER (WHERE b.post_tested = 1)'),
        )
        blocks = {'registrations': block(
            'registrations', select(valid, fields), self.MAIN + self.DETAILS,
            engine.groupings(self.MAIN, self.DETAILS, self.EXTRA), measures)}

        querysets, fields_list = [], []
        services = [(label, Q(**{field + '__iexact': 'yes'})) for label, field in self.SERVICES]
        services.append(('Digital platform', Q(using_digital_platform__istartswith='yes')))
        for label, condition in services:
            querysets.append(valid.filter(condition))
            fields_list.append(dict(self._child(reference_year), service=Value(label, output_field=CharField())))
        blocks['services'] = block(
            'services', select_union(querysets, fields_list), ('service',) + self.SUBGROUPS,
            engine.groupings(('service', 'partner', 'governorate'), ('sex', 'age_group')))

        fields = {
            'person': F('school_id'),
            'partner': F('partner_id'),
            'governorate': F('governorate_id'),
            'district': F('district_id'),
            'site_type': Coalesce('school__type', Value(NOT_SPECIFIED)),
        }
        blocks['sites'] = block(
            'sites', select(valid.filter(school__isnull=False), fields),
            ('partner', 'governorate', 'district', 'site_type'),
            engine.groupings(('partner', 'governorate'), ('district', 'site_type')))

        # teachers of the round; a school's partners are the partners that list it
        fields = {
            'person': F('id'),
            'partner': F('school__partner_schools__id'),
            'governorate': F('school__governorate_id'),
            'sex': sex('sex'),
            'assignment': Coalesce('teacher_assignment', Value(NOT_SPECIFIED)),
            'active': Coalesce('is_active_current_round', Value(NOT_SPECIFIED)),
        }
        blocks['staff'] = block(
            'staff', select(Teacher.objects.filter(round=the_round), fields),
            ('partner', 'governorate', 'sex', 'assignment', 'active'),
            engine.groupings(('partner', 'governorate'), ('sex', 'assignment', 'active')))

        attendance = CLMAttendanceStudent.objects.filter(
            attendance_day__round_id=the_round.id,
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

        schools = School.objects.filter(id__in=ids_in(blocks, 'school'))
        return {
            'format': FORMAT_VERSION,
            'programme': self.name,
            'label': self.label,
            'year': the_round.name,
            'generated_at': timezone.now().isoformat(),
            'counts': COUNTS,
            'rounds': [{'id': the_round.id, 'name': the_round.name, 'start_date': _iso(start),
                        'end_date': _iso(the_round.end_date_bridging),
                        'current': the_round.current_round_bridging}],
            'partners': partners(ids_in(blocks, 'partner')),
            'locations': locations(ids_in(blocks, 'governorate') | ids_in(blocks, 'district')
                                   | ids_in(blocks, 'cadaster')),
            'sites': [{'id': s.id, 'name': s.name, 'number': s.number, 'governorate': s.governorate_id,
                       'district': s.district_id, 'type': s.type} for s in schools],
            'nationalities': named(Nationality, ids_in(blocks, 'nationality')),
            'disabilities': named(Disability, ids_in(blocks, 'disability')),
            'blocks': blocks,
        }


COUNTS = 'unique children per grouping (attendance: days), no personal data'
PRESENT = Case(When(attended__iexact='yes', then=Value(1)), default=Value(0), output_field=IntegerField())
ATTENDANCE = (('days_recorded', 'COUNT(*)'), ('days_attended', 'SUM(b.present)'))


def _flag(condition):
    return Case(When(condition, then=Value(1)), default=Value(0), output_field=IntegerField())


def _iso(value):
    return value.isoformat() if isinstance(value, (datetime.date, datetime.datetime)) else None


PROGRAMMES = {p.name: p for p in (Makani(), Bridging())}
