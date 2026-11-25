"""View mode: the view, not the registration, decides the year's registrations and their partner and site.

* A view may give a registration of the previous year a round of this year (the key check still passes when
  99% of the rows, here a lower threshold, keep the registration's round). The registration counts in the year
  with its own round, so every round id of the counts must be in the payload's ``rounds``, with its name, and
  ``in_year`` false when it is not a round of the year (Bridging already did so; Makani now too).
* A view may give a registration another partner and centre (Makani) or partner and school (Bridging) than
  its own. ``enrolment_age``, Bridging's ``enrolment`` and the unique-children groupings of ``EXTRA`` count with
  the view's values: they match a brute-force count over the view.

The fixtures are those of test_unique_groupings (children "Secret", partners "Example ..."): no real name.
"""

from collections import Counter

import pytest

from student_registration.clm.models import Bridging
from student_registration.figures import education
from student_registration.mscc import models as m

from .test_unique_groupings import (  # noqa: F401 (dirasa, makani, places: fixtures)
    YEAR,
    dirasa,
    facts,
    grouping,
    makani,
    places,
    run,
    unique_by,
)

pytestmark = pytest.mark.django_db


def round_ids_counted(payload, programme):
    """Every round id in the programme's round cubes and in the registrations block's ``round`` grouping."""
    cubes = ('enrolment_age',) if programme == 'mscc' else ('enrolment',)
    found = {key[0] for key in grouping(payload['blocks']['registrations'], 'round')}
    for name in cubes:
        cube = payload['cubes'][name]
        at = cube['dims'].index('round')
        found |= {row[at] for row in cube['rows']}
    return found - {None}


# --------------------------------------------------------------------- 1. rounds of another year
def test_makani_lists_a_round_of_another_year_that_the_view_counts(request, settings):
    """The stand-in view gives the registration of the year before a round of this year: it counts in this
    year, with its own round, and that round is listed (``in_year`` false) with its name."""
    data = request.getfixturevalue('makani')
    settings.FIGURES_POWER_BI_MIN_MATCH = 0.85  # 9 of the 10 rows keep the registration's round
    late = m.Registration.objects.get(round__year=YEAR - 1)
    run("CREATE VIEW vw_mscc_data AS SELECT r.id, "
        "CASE WHEN r.id = %d THEN %d ELSE r.round_id END AS round_id, r.partner_id, r.center_id, r.deleted "
        "FROM %s r WHERE r.round_id IS NOT NULL AND r.type IS DISTINCT FROM 'TLS'"
        % (late.id, data['round_1'].id, m.Registration._meta.db_table))
    payload = education.PROGRAMMES['mscc'].build(str(YEAR))
    assert payload['power_bi']['base']['mode'] == 'view', payload['power_bi']['base']

    counted = round_ids_counted(payload, 'mscc')
    assert counted == {data['round_1'].id, data['round_2'].id, late.round_id}  # counted with its own round
    listed = {r['id']: r for r in payload['rounds']}
    assert counted <= set(listed), (sorted(counted), sorted(listed))
    assert listed[late.round_id]['name'] == late.round.name
    assert listed[late.round_id]['in_year'] is False and listed[late.round_id]['year'] == YEAR - 1
    for the_round in (data['round_1'], data['round_2']):
        assert listed[the_round.id]['in_year'] is True
    assert len(payload['rounds']) == len(listed) == 3  # each round once
    by_round = Counter()
    cube = payload['cubes']['enrolment_age']
    for row in cube['rows']:
        by_round[row[cube['dims'].index('round')]] += row[len(cube['dims'])]
    assert by_round[late.round_id] == 1


def test_makani_rounds_of_the_year_only_when_the_view_keeps_them(request):
    """Without such a registration, the rounds listed are the year's, each ``in_year``."""
    data = request.getfixturevalue('makani')
    run("CREATE VIEW vw_mscc_data AS SELECT r.id, r.round_id, r.partner_id, r.center_id, r.deleted FROM %s r "
        "WHERE r.round_id IS NOT NULL" % m.Registration._meta.db_table)
    payload = education.PROGRAMMES['mscc'].build(str(YEAR))
    assert payload['power_bi']['base']['mode'] == 'view'
    assert [(r['id'], r['in_year']) for r in payload['rounds']] == [
        (data['round_1'].id, True), (data['round_2'].id, True)]
    assert round_ids_counted(payload, 'mscc') == {r['id'] for r in payload['rounds']}


def test_bridging_lists_a_round_of_another_year_that_the_view_counts(request, settings):
    """The same case for Bridging, which already listed it: every counted round is listed."""
    data = request.getfixturevalue('dirasa')
    settings.FIGURES_POWER_BI_MIN_MATCH = 0.85
    late = Bridging.objects.exclude(round__in=[data['round_1'], data['round_2']]).get()
    run('CREATE VIEW vw_bridging_data AS SELECT b.id, '
        'CASE WHEN b.id = %d THEN %d ELSE b.round_id END AS round_id, b.partner_id, b.school_id, b.deleted '
        'FROM %s b' % (late.id, data['round_1'].id, Bridging._meta.db_table))
    payload = education.PROGRAMMES['bridging'].build(str(YEAR))
    assert payload['power_bi']['base']['mode'] == 'view', payload['power_bi']['base']
    counted = round_ids_counted(payload, 'bridging')
    assert late.round_id in counted
    listed = {r['id']: r for r in payload['rounds']}
    assert counted <= set(listed)
    assert listed[late.round_id]['in_year'] is False and listed[late.round_id]['name'] == late.round.name


# ------------------------------------------------------------------ 2. the view's partner and site
MOVED = 'k1'  # the registration the stand-in view gives another partner and site


def view_with_other_values(programme, data):
    """A stand-in view that keeps every registration of a round but gives MOVED partner B and another site
    (Makani: centre 2, in the same governorate as its own centre 1; Bridging: school 3). Returns the
    brute-force rows over the view: the registrations' facts with the view's partner and site."""
    moved = data['regs'][MOVED]
    if programme == 'mscc':
        site = m.Registration.objects.filter(center__name='Example Centre 2').values_list('center_id', flat=True)[0]
        run("CREATE VIEW vw_mscc_data AS SELECT r.id, r.round_id, "
            "CASE WHEN r.id = %(id)d THEN %(partner)d ELSE r.partner_id END AS partner_id, "
            "CASE WHEN r.id = %(id)d THEN %(site)d ELSE r.center_id END AS center_id, r.deleted "
            "FROM %(table)s r WHERE r.round_id IS NOT NULL AND r.type IS DISTINCT FROM 'TLS'"
            % {'id': moved.id, 'partner': data['partner_b'].id, 'site': site,
               'table': m.Registration._meta.db_table})
    else:
        site = Bridging.objects.filter(school__name='Example School 3').values_list('school_id', flat=True)[0]
        run('CREATE VIEW vw_bridging_data AS SELECT b.id, b.round_id, '
            'CASE WHEN b.id = %(id)d THEN %(partner)d ELSE b.partner_id END AS partner_id, '
            'CASE WHEN b.id = %(id)d THEN %(site)d ELSE b.school_id END AS school_id, b.deleted FROM %(table)s b'
            % {'id': moved.id, 'partner': data['partner_b'].id, 'site': site, 'table': Bridging._meta.db_table})
    rows = []
    for key, registration in data['regs'].items():
        row = facts(programme, registration)
        if key == MOVED:
            assert (row['partner'], row['site']) != (data['partner_b'].id, site)
            row.update(partner=data['partner_b'].id, site=site)
        rows.append(row)
    return rows


def summed(cube, dims):
    """Registrations per combination of ``dims``, summed over the cube's other dimensions."""
    measure = len(cube['dims']) + cube['measures'].index('registrations')
    out = Counter()
    for row in cube['rows']:
        out[tuple(row[cube['dims'].index(d)] for d in dims)] += row[measure]
    return dict(out)


def counted_by(rows, keys):
    return dict(Counter(tuple(row[k] for k in keys) for row in rows))


@pytest.mark.parametrize('programme', ['mscc', 'bridging'])
def test_the_new_counts_take_partner_and_site_from_the_view(programme, request):
    data = request.getfixturevalue('makani' if programme == 'mscc' else 'dirasa')
    rows = view_with_other_values(programme, data)
    payload = education.PROGRAMMES[programme].build(str(YEAR))
    base = payload['power_bi']['base']
    assert base['mode'] == 'view', base
    definition = education.PROGRAMMES[programme].__class__
    site = 'center' if programme == 'mscc' else 'school'
    assert set(base['overrides']) == {'partner', site}

    # the age group cube (Makani's enrolment_age, Bridging's enrolment): every dimension, the view's values
    cube = payload['cubes']['enrolment_age' if programme == 'mscc' else 'enrolment']
    dims = ['partner', 'governorate', site, 'sex', 'nationality', 'disability', 'age_group', 'round']
    keys = [{'center': 'site', 'school': 'site'}.get(d, d) for d in dims]
    assert summed(cube, dims) == counted_by(rows, keys)
    assert summed(cube, ['partner', site]) == counted_by(rows, ['partner', 'site'])

    # every grouping appended to EXTRA: unique children, the view's values
    registrations = payload['blocks']['registrations']
    extra = 2 if programme == 'bridging' else 0  # Bridging's block also counts pre- and post-tested children
    for new in definition.EXTRA[-5:]:
        names = tuple(sorted(new))
        keys = tuple({'center': 'site', 'school': 'site', 'registration_level': 'level'}.get(n, n) for n in names)
        assert grouping(registrations, *names) == {k: [v] + [0] * extra
                                                   for k, v in unique_by(rows, *keys).items()}, new
    # partner B now has the moved child in its site
    moved = data['regs'][MOVED]
    partner_site = grouping(registrations, 'partner', site, 'sex')
    position = sorted(('partner', site, 'sex'))
    moved_sex = facts(programme, moved)['sex']
    found = {(k[position.index('partner')], k[position.index(site)]) for k, _row in partner_site.items()
             if k[position.index('sex')] == moved_sex}
    assert (data['partner_b'].id, rows[list(data['regs']).index(MOVED)]['site']) in found
