"""Unique children for the common combinations, and registrations by age group and Makani round.

The ``registrations`` block answers a unique-children question only from the grouping that matches it exactly,
so the combinations NeuroDB asks for (centre + sex, partner + sex + nationality...) are groupings of their own
(``EXTRA``). The registrations are counted by age group and round in a cube, defined as the same dimensions of
the registrations block. Every check runs in view mode (a stand-in view under the real name, which leaves one
counted registration out so that the view, not the rule, decides) and in rule mode (no view).

The children are named "Secret", the partners "Example ...": no real name.
"""

import datetime
import json
from collections import Counter, defaultdict

import pytest
from django.db import connection

from student_registration.child.models import Child
from student_registration.clm.models import Bridging, Disability
from student_registration.figures import education, engine
from student_registration.locations.models import Center, Location, LocationType
from student_registration.mscc import models as m
from student_registration.schools.models import CLMRound, PartnerOrganization, School
from student_registration.students.models import Nationality, Student

pytestmark = pytest.mark.django_db

YEAR = 2025

# the groupings this change adds, at the end of EXTRA (never renamed, reordered or removed)
MAKANI_NEW = (('center', 'sex'), ('partner', 'center', 'sex'), ('partner', 'sex', 'nationality'),
              ('partner', 'sex', 'disability'), ('governorate', 'sex', 'nationality'))
BRIDGING_NEW = (('school', 'sex'), ('partner', 'school', 'sex'), ('partner', 'sex', 'nationality'),
                ('partner', 'sex', 'disability'), ('partner', 'sex', 'registration_level'))
# EXTRA as it was before this change: still its first groupings, in the same order
MAKANI_EXTRA_BEFORE = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
                       ('disability', 'sex'), ('nationality', 'sex'), ('district', 'sex'))
BRIDGING_EXTRA_BEFORE = (('sex', 'age_group'), ('partner', 'sex', 'age_group'), ('governorate', 'sex', 'age_group'),
                         ('registration_level', 'sex'), ('disability', 'sex'), ('nationality', 'sex'),
                         ('learning_result', 'sex'), ('district', 'sex'), ('round', 'sex'))
MAKANI_ENROLMENT_BEFORE = ('center', 'partner', 'governorate', 'sex', 'nationality', 'disability', 'caregiver',
                           'working', 'programme', 'education_status', 'package', 'id_type', 'malnutrition', 'delay')
BRIDGING_ENROLMENT_BEFORE = ('school', 'partner', 'governorate', 'sex', 'nationality', 'disability', 'level',
                             'learning_result', 'barrier', 'round')


def run(sql):
    with connection.cursor() as cursor:
        cursor.execute(sql)


def age_group(born):
    """The age group in YEAR of a birth year stored as text, as education.age_group gives it."""
    if not (born or '').isdigit() or len(born) != 4:
        return education.NOT_SPECIFIED
    born = int(born)
    if born > YEAR or born < 1900:
        return education.NOT_SPECIFIED
    age = YEAR - born
    for limit, label in ((6, 'Under 6'), (10, '6-9'), (15, '10-14'), (18, '15-17')):
        if age < limit:
            return label
    return '18 and over'


def grouping(block, *by):
    """{values: measures} of the grouping ``by`` (in any order) of a block."""
    by = tuple(sorted(by))
    found = next(g for g in block['figures'] if tuple(g['by']) == by)
    return {tuple(row[:len(by)]): row[len(by):] for row in found['rows']}


def cube_with(payload, dimension):
    """The registrations cube that has ``dimension`` (``enrolment``, or ``enrolment_age`` when one is sent)."""
    found = [c for c in payload['cubes'].values() if dimension in c['dims'] and 'registrations' in c['measures']]
    assert len(found) == 1, sorted(payload['cubes'])
    return found[0]


def registrations_by(cube, dimension):
    """Registrations per value of ``dimension``, summed over the cube's other dimensions."""
    at, measure = cube['dims'].index(dimension), len(cube['dims']) + cube['measures'].index('registrations')
    out = Counter()
    for row in cube['rows']:
        out[row[at]] += row[measure]
    return dict(out)


# ------------------------------------------------------------------------------------- data
@pytest.fixture
def places():
    gov = LocationType.objects.create(name='Governorate')
    north = Location.objects.create(name='Example North', p_code='EX1', type=gov)
    south = Location.objects.create(name='Example South', p_code='EX2', type=gov)
    return {'north': north, 'south': south,
            'nat_a': Nationality.objects.create(name='Example A', name_en='Example A'),
            'nat_b': Nationality.objects.create(name='Example B', name_en='Example B'),
            'dis_no': Disability.objects.create(name='No', name_en='No', active=True),
            'dis_yes': Disability.objects.create(name='Yes', name_en='Yes', active=True)}


@pytest.fixture
def makani(places):
    """Two partners, three centres, two rounds in YEAR and one in the year before. Child ``k2`` is in two
    centres of partner A; child ``k4`` is with both partners. The deleted registration and the one of the year
    before never count."""
    partner_a = PartnerOrganization.objects.create(name='Example Partner A', is_makani=True)
    partner_b = PartnerOrganization.objects.create(name='Example Partner B', is_makani=True)
    round_1 = m.Round.objects.create(name='Round 1 %d' % YEAR, year=YEAR, current_year=True,
                                     start_date=datetime.date(YEAR, 1, 10))
    round_2 = m.Round.objects.create(name='Round 2 %d' % YEAR, year=YEAR, start_date=datetime.date(YEAR, 6, 1))
    before = m.Round.objects.create(name='Round 1 %d' % (YEAR - 1), year=YEAR - 1)
    c1 = Center.objects.create(name='Example Centre 1', partner=partner_a, governorate=places['north'])
    c2 = Center.objects.create(name='Example Centre 2', partner=partner_a, governorate=places['north'])
    c3 = Center.objects.create(name='Example Centre 3', partner=partner_b, governorate=places['south'])

    def child(gender, born, nationality='nat_a', disability='dis_no'):
        return Child.objects.create(first_name='Secret', gender=gender, birthday_year=born,
                                    nationality=places[nationality], disability=places[disability])

    k1, k2 = child('Female', '2020'), child('Male', '2017', 'nat_b')
    k3, k4 = child('Female', '2012', disability='dis_yes'), child('Male', '2009')
    k5, k6 = child('Female', '2000', 'nat_b'), child('Male', 'n/a')
    k7, k8 = child('Female', '2011'), child('Male', '2015')

    def reg(kid, partner, center, the_round, **fields):
        return m.Registration.objects.create(child=kid, partner=partner, center=center, round=the_round,
                                             type='Core-Package', **fields)

    regs = {
        'k1': reg(k1, partner_a, c1, round_1),
        'k2_c1': reg(k2, partner_a, c1, round_1),
        'k2_c2': reg(k2, partner_a, c2, round_2),  # the same child in another centre of the same partner
        'k3': reg(k3, partner_a, c2, round_2),
        'k4_b': reg(k4, partner_b, c3, round_1),
        'k4_a': reg(k4, partner_a, c1, round_2),  # the same child with the other partner
        'k5': reg(k5, partner_a, c1, round_1),
        'k6': reg(k6, partner_b, c3, round_2),
    }
    reg(k7, partner_a, c1, round_1, deleted=True)  # deleted: never counts
    reg(k8, partner_a, c1, before)  # the year before
    return {'partner_a': partner_a, 'partner_b': partner_b, 'round_1': round_1, 'round_2': round_2, 'regs': regs}


@pytest.fixture
def dirasa(places):
    """Two partners, three schools, two Bridging rounds starting in YEAR and one the year before."""
    partner_a = PartnerOrganization.objects.create(name='Example Partner A', is_dirasa=True)
    partner_b = PartnerOrganization.objects.create(name='Example Partner B', is_dirasa=True)
    round_1 = CLMRound.objects.create(name='Bridging %d A' % YEAR, current_round_bridging=True,
                                      start_date_bridging=datetime.date(YEAR, 2, 1))
    round_2 = CLMRound.objects.create(name='Bridging %d B' % YEAR, start_date_bridging=datetime.date(YEAR, 9, 1))
    before = CLMRound.objects.create(name='Bridging %d' % (YEAR - 1),
                                     start_date_bridging=datetime.date(YEAR - 1, 9, 1))
    s1 = School.objects.create(number='9001', name='Example School 1', governorate=places['north'])
    s2 = School.objects.create(number='9002', name='Example School 2', governorate=places['north'])
    s3 = School.objects.create(number='9003', name='Example School 3', governorate=places['south'])

    def student(sex, born, nationality='nat_a'):
        return Student.objects.create(first_name='Secret', sex=sex, birthday_year=born,
                                      nationality=places[nationality])

    k1, k2 = student('Female', '2018'), student('Male', '2016', 'nat_b')
    k3, k4 = student('Female', '2012'), student('Male', '2009')
    k5, k6 = student('Female', '2006', 'nat_b'), student('Male', '')
    k7, k8 = student('Female', '2013'), student('Male', '2014')

    def reg(kid, partner, school, the_round, level='level_one', disability='dis_no', **fields):
        governorate = school.governorate
        return Bridging.objects.create(student=kid, partner=partner, school=school, round=the_round,
                                       governorate=governorate, registration_level=level,
                                       disability=places[disability], **fields)

    regs = {
        'k1': reg(k1, partner_a, s1, round_1),
        'k2_s1': reg(k2, partner_a, s1, round_1, level='level_two'),
        'k2_s2': reg(k2, partner_a, s2, round_2, level='level_two'),  # another school of the same partner
        'k3': reg(k3, partner_a, s2, round_2, disability='dis_yes'),
        'k4_b': reg(k4, partner_b, s3, round_1),
        'k4_a': reg(k4, partner_a, s1, round_2, level='level_three'),  # the same child with the other partner
        'k5': reg(k5, partner_a, s1, round_1),
        'k6': reg(k6, partner_b, s3, round_2),
    }
    reg(k7, partner_a, s1, round_1, deleted=True)  # deleted: never counts
    reg(k8, partner_a, s1, before)  # the year before
    return {'partner_a': partner_a, 'partner_b': partner_b, 'round_1': round_1, 'round_2': round_2, 'regs': regs}


# ------------------------------------------------------------------------------------ modes
LEFT_OUT = 'k5'  # the counted registration the stand-in view leaves out


def counted_registrations(data, mode):
    """The registrations the payload must count: the rule's, less the one the view leaves out in view mode."""
    return [r for key, r in data['regs'].items() if not (mode == 'view' and key == LEFT_OUT)]


def build(programme, data, mode):
    """The payload of YEAR in ``mode``; in view mode, a stand-in view that keeps every registration of a round
    (deleted ones too, as the real views do) except LEFT_OUT."""
    if mode == 'view':
        left_out = data['regs'][LEFT_OUT].id
        if programme == 'mscc':
            run("CREATE VIEW vw_mscc_data AS SELECT r.id, r.round_id, r.partner_id, r.center_id, r.deleted "
                "FROM %s r WHERE r.round_id IS NOT NULL AND r.type IS DISTINCT FROM 'TLS' AND r.id <> %d"
                % (m.Registration._meta.db_table, left_out))
        else:
            run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, b.partner_id, b.school_id, b.deleted '
                'FROM %s b WHERE b.id <> %d' % (Bridging._meta.db_table, left_out))
    payload = education.PROGRAMMES[programme].build(str(YEAR))
    assert payload['power_bi']['base']['mode'] == mode, payload['power_bi']['base']
    return payload


def facts(programme, registration):
    """(child, partner, site, sex, nationality, disability, level, age group, round) of a registration, read
    from the records themselves: the brute-force side of the checks."""
    if programme == 'mscc':
        kid = registration.child
        return {'person': kid.id, 'partner': registration.partner_id, 'site': registration.center_id,
                'governorate': registration.center.governorate_id, 'sex': kid.gender,
                'nationality': kid.nationality_id, 'disability': kid.disability_id, 'level': None,
                'age_group': age_group(kid.birthday_year), 'round': registration.round_id}
    kid = registration.student
    return {'person': kid.id, 'partner': registration.partner_id, 'site': registration.school_id,
            'governorate': registration.governorate_id, 'sex': kid.sex, 'nationality': kid.nationality_id,
            'disability': registration.disability_id, 'level': registration.registration_level,
            'age_group': age_group(kid.birthday_year), 'round': registration.round_id}


def unique_by(rows, *keys):
    """Distinct children per combination of ``keys``, by brute force."""
    seen = defaultdict(set)
    for row in rows:
        seen[tuple(row[k] for k in keys)].add(row['person'])
    return {k: len(v) for k, v in seen.items()}


PROGRAMMES = {
    'mscc': {'fixture': 'makani', 'site': 'center', 'new': MAKANI_NEW, 'extra_before': MAKANI_EXTRA_BEFORE,
             'enrolment_before': MAKANI_ENROLMENT_BEFORE, 'definition': education.Makani},
    'bridging': {'fixture': 'dirasa', 'site': 'school', 'new': BRIDGING_NEW, 'extra_before': BRIDGING_EXTRA_BEFORE,
                 'enrolment_before': BRIDGING_ENROLMENT_BEFORE, 'definition': education.Bridging},
}
CASES = [(p, mode) for p in PROGRAMMES for mode in ('view', 'rule')]


@pytest.fixture
def case(request):
    programme, mode = request.param
    spec = PROGRAMMES[programme]
    data = request.getfixturevalue(spec['fixture'])
    rows = [facts(programme, r) for r in counted_registrations(data, mode)]
    return {'programme': programme, 'mode': mode, 'spec': spec, 'data': data, 'rows': rows,
            'payload': build(programme, data, mode)}


# ------------------------------------------------------------------------------------ tests
@pytest.mark.parametrize('programme', sorted(PROGRAMMES))
def test_existing_groupings_and_dimensions_keep_their_place(programme):
    spec = PROGRAMMES[programme]
    definition = spec['definition']
    extra_before = len(spec['extra_before'])
    assert definition.EXTRA[:extra_before] == spec['extra_before']
    assert definition.EXTRA[extra_before:] == spec['new']
    before = engine.groupings(definition.MAIN, definition.DETAILS, spec['extra_before'])
    after = engine.groupings(definition.MAIN, definition.DETAILS, definition.EXTRA)
    assert after[:len(before)] == before
    assert definition.ENROLMENT[:len(spec['enrolment_before'])] == spec['enrolment_before']


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_each_new_grouping_is_in_the_registrations_block(case):
    found = [tuple(g['by']) for g in case['payload']['blocks']['registrations']['figures']]
    for new in case['spec']['new']:
        assert tuple(sorted(new)) in found, new
    assert len(found) == len(set(found))


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_a_partners_unique_children_by_sex_add_up_to_its_unique_total(case):
    registrations = case['payload']['blocks']['registrations']
    partner = case['data']['partner_a'].id
    total = grouping(registrations, 'partner')[(partner,)][0]
    by_sex = {sex: row[0] for (p, sex), row in grouping(registrations, 'partner', 'sex').items() if p == partner}
    assert set(by_sex) == {'Male', 'Female'}  # no child of partner A has another sex
    assert by_sex['Male'] <= total and by_sex['Female'] <= total
    assert by_sex['Male'] + by_sex['Female'] == total
    expected = unique_by(case['rows'], 'partner')[(partner,)]
    assert total == expected  # k2 counts once although in two centres
    # the three-dimension groupings of the partner add up the same way over their third dimension
    for third in ('nationality', 'disability') + (('registration_level',) if case['programme'] == 'bridging' else ()):
        rows = grouping(registrations, 'partner', 'sex', third)
        position = sorted(('partner', 'sex', third))
        for sex in ('Male', 'Female'):
            parts = [row[0] for key, row in rows.items()
                     if key[position.index('partner')] == partner and key[position.index('sex')] == sex]
            assert sum(parts) == by_sex[sex], (third, sex)  # each child has one value of the third dimension


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_site_and_sex_unique_children_match_a_brute_force_count(case):
    registrations = case['payload']['blocks']['registrations']
    site = case['spec']['site']
    expected = unique_by(case['rows'], 'site', 'sex')
    found = grouping(registrations, site, 'sex')
    position = sorted((site, 'sex'))
    assert {(key[position.index(site)], key[position.index('sex')]): row[0] for key, row in found.items()} == expected
    # partner + site + sex: the same children, each site under its partner
    expected = unique_by(case['rows'], 'partner', 'site', 'sex')
    found = grouping(registrations, 'partner', site, 'sex')
    position = sorted(('partner', site, 'sex'))
    assert {(key[position.index('partner')], key[position.index(site)], key[position.index('sex')]): row[0]
            for key, row in found.items()} == expected


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_the_other_new_groupings_match_a_brute_force_count(case):
    registrations = case['payload']['blocks']['registrations']
    for new in case['spec']['new']:
        names = tuple(sorted(new))
        keys = tuple({'center': 'site', 'school': 'site', 'registration_level': 'level'}.get(n, n) for n in names)
        expected = unique_by(case['rows'], *keys)
        if 'level' in keys:  # the block shows a missing level as "Not specified" (none here)
            assert all(k[keys.index('level')] for k in expected)
        assert grouping(registrations, *names) == {k: [v] + ([0, 0] if case['programme'] == 'bridging' else [])
                                                   for k, v in expected.items()}, new


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_registrations_by_age_group_add_up_to_the_total(case):
    payload = case['payload']
    cube = cube_with(payload, 'age_group')
    total = sum(registrations_by(payload['cubes']['enrolment'], 'partner').values())
    by_age = registrations_by(cube, 'age_group')
    assert sum(by_age.values()) == total == len(case['rows'])
    assert by_age == dict(Counter(row['age_group'] for row in case['rows']))
    # every age group of the cube is one the registrations block gives, the same labels
    block_groups = {key[0] for key in grouping(payload['blocks']['registrations'], 'age_group')}
    assert set(by_age) == block_groups
    assert set(by_age) <= set(education.AGE_GROUPS)
    assert education.NOT_SPECIFIED in by_age  # the child with no usable birth year


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_registrations_by_round_add_up_to_the_total(case):
    payload = case['payload']
    cube = cube_with(payload, 'round') if case['programme'] == 'mscc' else payload['cubes']['enrolment']
    total = sum(registrations_by(payload['cubes']['enrolment'], 'partner').values())
    by_round = registrations_by(cube, 'round')
    assert sum(by_round.values()) == total == len(case['rows'])
    assert by_round == dict(Counter(row['round'] for row in case['rows']))
    assert set(by_round) == {case['data']['round_1'].id, case['data']['round_2'].id}
    assert set(by_round) == {key[0] for key in grouping(payload['blocks']['registrations'], 'round')}


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_age_group_and_round_together_add_up(case):
    """A cube row holds age group and round at once, so a reader can filter on both: summed over the rest they
    match the brute-force count of registrations per (age group, round)."""
    payload = case['payload']
    cube = cube_with(payload, 'age_group')
    if 'round' not in cube['dims']:
        pytest.fail('the age group cube has no round: %s' % cube['dims'])
    age_at, round_at = cube['dims'].index('age_group'), cube['dims'].index('round')
    measure = len(cube['dims']) + cube['measures'].index('registrations')
    found = Counter()
    for row in cube['rows']:
        found[(row[age_at], row[round_at])] += row[measure]
    assert dict(found) == dict(Counter((row['age_group'], row['round']) for row in case['rows']))


@pytest.mark.parametrize('case', CASES, indirect=True, ids=['-'.join(c) for c in CASES])
def test_the_payload_holds_counts_only(case):
    text = json.dumps(case['payload'])
    assert 'Secret' not in text and 'first_name' not in text and 'birthday' not in text
    assert case['payload']['format'] == 4


@pytest.mark.parametrize('mode', ['view', 'rule'])
def test_makanis_age_cube_agrees_with_the_enrolment_cube(makani, mode):
    """``enrolment_age`` (registrations by age group and round, a cube of its own) and ``enrolment`` count the
    same registrations: summed over the dimensions they share they give the same rows, partner and centre
    from the view in view mode. ``enrolment`` keeps its dimensions."""
    payload = build('mscc', makani, mode)
    enrolment, age = payload['cubes']['enrolment'], payload['cubes']['enrolment_age']
    assert enrolment['dims'] == list(MAKANI_ENROLMENT_BEFORE)
    assert age['dims'] == list(education.Makani.ENROLMENT_AGE) and age['measures'] == ['registrations']
    shared = [d for d in age['dims'] if d in enrolment['dims']]
    assert shared == ['partner', 'governorate', 'center', 'sex', 'nationality', 'disability']

    def summed(cube):
        out = Counter()
        measure = len(cube['dims']) + cube['measures'].index('registrations')
        for row in cube['rows']:
            out[tuple(row[cube['dims'].index(d)] for d in shared)] += row[measure]
        return dict(out)

    assert summed(age) == summed(enrolment)
    assert sum(summed(age).values()) == len(counted_registrations(makani, mode))
    assert list(payload['cubes']) == ['enrolment', 'staff', 'enrolment_age']  # appended
