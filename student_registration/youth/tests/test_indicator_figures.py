"""The youth indicator figures for NeuroDB: unique youth per grouping, counts only, service access."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from student_registration.adolescent.models import Adolescent
from student_registration.locations.models import Location, LocationType
from student_registration.schools.models import PartnerOrganization
from student_registration.students.models import Nationality
from student_registration.youth import indicator_figures
from student_registration.youth.models import (
    Donor,
    EnrolledPrograms,
    MasterProgram,
    ProgramDocument,
    ProgramDocumentIndicator,
    Registration,
    SubProgram,
    Year,
)

URL = '/api/youth/indicator-figures/'


@pytest.fixture
def data(db):
    year = Year.objects.create(name='2026', current_year=True)
    gov_type = LocationType.objects.create(name='Governorate')
    district_type = LocationType.objects.create(name='District')
    akkar = Location.objects.create(name='Akkar', p_code='LB1', type=gov_type)
    beirut = Location.objects.create(name='Beirut', p_code='LB6', type=gov_type)
    halba = Location.objects.create(name='Halba', p_code='LB11', type=district_type, parent=akkar)
    syrian = Nationality.objects.create(name='Syrian', name_en='Syrian')
    partner = PartnerOrganization.objects.create(name='Youth Partner', is_youth=True)
    other_partner = PartnerOrganization.objects.create(name='Second Partner', is_youth=True)
    eu = Donor.objects.create(name='EU', active=True)
    japan = Donor.objects.create(name='Japan', active=True)
    skills = MasterProgram.objects.create(number='1', name='Skills', active=True)
    digital = SubProgram.objects.create(master_program=skills, number='1.1', name='Digital skills')
    life = SubProgram.objects.create(master_program=skills, number='1.2', name='Life skills')
    pd = ProgramDocument.objects.create(
        year=year, partner=partner, project_code='LEB/PCA2026001', project_name='Youth skills'
    )
    pd.donors.set([eu, japan])
    ProgramDocumentIndicator.objects.create(
        program_document=pd, master_indicator=skills, sub_indicator=digital, target=100
    )

    def youth(gender, born, gov=akkar, district=halba, deleted=False, reg_partner=partner):
        person = Adolescent.objects.create(
            first_name='x', gender=gender, birthday_year=str(born), nationality=syrian,
            governorate=gov, district=district,
        )
        return Registration.objects.create(
            year=year, adolescent=person, partner=reg_partner, deleted=deleted
        )

    def enrol(registration, sub, donor, **place):
        return EnrolledPrograms.objects.create(
            registration=registration, master_program=sub.master_program, sub_program=sub, donor=donor,
            program_document=pd, **place
        )

    a = youth('Female', 2008)  # 18 in 2026
    b = youth('Male', 2010)  # 16
    c = youth('Female', 2004, gov=beirut, district=None, reg_partner=other_partner)  # 22
    gone = youth('Male', 2009, deleted=True)
    enrol(a, digital, eu)  # "same location": the youth's address (Akkar, Halba)
    enrol(a, life, japan)  # a second sub indicator: still one youth for the master indicator
    enrol(a, digital, eu)  # enrolled twice in the same sub indicator: counted once
    enrol(b, digital, eu, governorate=beirut)  # enrolled in another place than home
    enrol(c, life, japan)
    enrol(gone, digital, eu)  # a deleted registration never counts
    return {
        'year': year, 'akkar': akkar, 'beirut': beirut, 'halba': halba, 'partner': partner,
        'other_partner': other_partner, 'eu': eu, 'japan': japan, 'skills': skills, 'digital': digital,
        'life': life, 'pd': pd,
    }


def table(payload, *by):
    grouping = next(g for g in payload['figures'] if g['by'] == sorted(by))
    return {tuple(row[:-1]): row[-1] for row in grouping['rows']}


def test_unique_youth_per_grouping(data):
    payload = indicator_figures.build(data['year'])
    assert table(payload)[()] == 3  # a, b, c; the deleted one is left out
    assert table(payload, 'master') == {(data['skills'].id,): 3}
    assert table(payload, 'sub') == {(data['digital'].id,): 2, (data['life'].id,): 2}
    assert table(payload, 'donor') == {(data['eu'].id,): 2, (data['japan'].id,): 2}
    assert table(payload, 'partner') == {(data['partner'].id,): 2, (data['other_partner'].id,): 1}
    # a counts in Akkar (home, same location), b where enrolled (Beirut), c at home (Beirut)
    assert table(payload, 'governorate') == {(data['akkar'].id,): 1, (data['beirut'].id,): 2}
    assert table(payload, 'sex') == {('Female',): 2, ('Male',): 1}
    assert table(payload, 'age_group') == {('15-17',): 1, ('18-24',): 2}


def test_groupings_combine_main_dimensions_with_one_detail(data):
    payload = indicator_figures.build(data['year'])
    by_donor_sub = table(payload, 'donor', 'sub')
    assert by_donor_sub[(data['digital'].id, data['eu'].id)] == 2
    assert by_donor_sub[(data['life'].id, data['japan'].id)] == 2
    assert len(indicator_figures.groupings()) == 16 * 7 + 1
    assert table(payload, 'program_document', 'sub') == {
        (data['pd'].id, data['digital'].id): 2, (data['pd'].id, data['life'].id): 2,
    }
    assert all(sorted(g['by']) == g['by'] for g in payload['figures'])


def test_payload_describes_what_it_counts_and_holds_no_personal_data(data):
    payload = indicator_figures.build(data['year'])
    assert payload['year'] == '2026'
    assert {i['name'] for i in payload['indicators']} == {'Skills', 'Digital skills', 'Life skills'}
    assert payload['program_documents'][0]['project_code'] == 'LEB/PCA2026001'
    assert payload['targets'] == [{
        'program_document': data['pd'].id, 'master': data['skills'].id, 'sub': data['digital'].id,
        'baseline': None, 'target': 100,
    }]
    assert {loc['p_code'] for loc in payload['locations']} == {'LB1', 'LB6', 'LB11'}
    text = str(payload)
    assert "'x'" not in text and 'first_name' not in text and 'adolescent' not in text


def test_age_group_rule():
    assert indicator_figures.age_group('2012', 2026) == 'Under 15'
    assert indicator_figures.age_group('2001', 2026) == '25 and over'
    assert indicator_figures.age_group(0, 2026) == 'Not specified'
    assert indicator_figures.age_group('abc', 2026) == 'Not specified'


def test_only_the_service_account_reads_the_figures(data):
    client = APIClient()
    assert client.get(URL).status_code in (401, 403)

    user_model = get_user_model()
    partner_user = user_model.objects.create_user(username='partner', password='x-pass-123456')
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=partner_user).key)
    assert client.get(URL).status_code == 403

    service = user_model.objects.create_user(username='neurodb', password='x-pass-123456')
    service.groups.add(Group.objects.create(name='NeuroDB API'))
    client.credentials(HTTP_AUTHORIZATION='Token ' + Token.objects.create(user=service).key)
    response = client.get(URL, {'year': '2026'})
    assert response.status_code == 200
    assert response.json()['figures']
    assert client.get(URL, {'year': '1999'}).status_code == 404
