
from student_registration.taskapp.celery import app

import json
import httplib
import datetime
from time import mktime
from django.core.serializers.json import DjangoJSONEncoder
from openpyxl import load_workbook


@app.task
def push_household_data(base_url, token, protocol='HTTPS'):

    wb = load_workbook(filename='BTS_Outreach_data_05022018.xlsx', read_only=True)
    ws = wb['Household']

    try:
        for row in ws.rows:
            if row[0].value == 'FORMID':
                continue
            data = {}
            data['form_id'] = row[0].value
            data['partner_name'] = row[1].value if row[1].value else 'None'
            data['governorate'] = row[2].value if row[2].value else 'None'
            data['district'] = row[3].value if row[3].value else 'None'
            data['village'] = row[4].value if row[4].value else 'None'
            data['name'] = row[5].value if row[5].value else 'None'
            data['phone_number'] = row[6].value if row[6].value else '000000'
            data['residence_type'] = row[7].value if row[7].value else 'None'
            data['p_code'] = row[8].value if row[8].value else 'None'
            data['address'] = row[9].value if row[9].value else 'None'
            data['number_of_children'] = row[10].value if row[10].value else '0'
            data['barcode_number'] = row[11].value if row[11].value else '0'

            post_data(protocol=protocol, url=base_url, apifunc='/api/household/', token=token, data=data)
    except Exception as ex:
        print("---------------")
        print("error: ", ex.message)
        print(json.dumps(data, cls=DjangoJSONEncoder))
        print("---------------")
        pass


@app.task
def update_household_data():
    from .models import HouseHold
    wb = load_workbook(filename='BTS_Outreach_data_05022018_original.xlsx', read_only=True)
    ws = wb['Householdinfo']

    try:
        for row in ws.rows:
            if row[0].value == 'FORMID':
                continue
            household = HouseHold.objects.get(form_id=row[0].value)
            household.interview_status = row[11].value
            household.save()

    except Exception as ex:
        print("---------------")
        print("error: ", ex.message)
        print("---------------")
        pass


@app.task
def push_children_data(base_url, token, protocol='HTTPS'):

    # NATIONALITIES = {
    #     'Syria': 1,
    #     'Iraq': 2,
    #     'Lebanon': 5,
    #     'Other': 6,
    #     'Palestine': 4
    # }
    ID_TYPES = {
        'None': 6,
        'UNHCR': 1,
        'Lebanese': 5,
        'Other': 5,
        'Syria': 3,
    }

    wb = load_workbook(filename='BTS_Outreach_data_05022018.xlsx', read_only=True)
    ws = wb['Individuals']

    try:
        for row in ws.rows:
            if row[0].value == 'FORMID':
                continue

            data = {}
            data['form_id'] = row[0].value
            data['first_name'] = row[1].value if row[1].value else 'None'
            data['father_name'] = row[2].value if row[2].value else 'None'
            data['last_name'] = row[3].value if row[3].value else 'None'
            data['mother_fullname'] = row[4].value if row[4].value else 'None'

            # data['mother_nationality'] = NATIONALITIES[row[5].value] if row[5].value in NATIONALITIES else 6
            data['mother_nationality'] = row[5].value if row[5].value else 6

            data['birthday_year'] = row[6].value if row[6].value else '1990'
            data['birthday_month'] = row[7].value if row[7].value else '1'
            data['birthday_day'] = row[8].value if row[8].value else '1'
            data['nationality'] = row[9].value if row[9].value else 6

            data['id_type'] = ID_TYPES[row[10].value] if row[10].value in ID_TYPES else 6

            data['id_number'] = row[11].value if row[11].value else '000000'  # ID_Num
            if row[13].value:  # Case_Individual_Num
                data['id_number'] = row[13].value
            elif row[14].value:  # ID_Individual_Num
                data['id_number'] = row[14].value
            elif row[12].value:  # UNHCR_Case_Num
                data['id_number'] = row[12].value

            data['sex'] = row[15].value if row[15].value else 'Male'

            post_data(protocol=protocol, url=base_url, apifunc='/api/child/', token=token, data=data)
    except Exception as ex:
        print("---------------")
        print("error: ", ex.message)
        print(json.dumps(data, cls=DjangoJSONEncoder))
        print("---------------")
        pass


@app.task
def update_children_data_2():
    from .models import Child
    wb = load_workbook(filename='BTS_Outreach_data_05022018_original_children.xlsx', read_only=True)
    ws = wb['IndividualInfo']
    ctr = 0

    for row in ws.rows:
        try:
            if row[0].value == 'FORMID':
                continue
            if not row[1].value or not row[2].value or not row[3].value:
                continue
            child = Child.objects.filter(
                form_id=row[0].value.strip(),
                first_name=row[1].value.strip(),
                father_name=row[2].value.strip(),
                last_name=row[3].value.strip(),
            ).first()
            if not child:
                ctr += 1
                continue

            child.last_edu_system = row[16].value
            child.last_school_formal_year = row[18].value
            child.last_education_year = row[19].value
            child.last_public_school_location = row[20].value
            child.last_informal_education = row[21].value
            child.not_enrolled_reasons = row[22].value.split(',') if row[22].value else []
            if row[23].value:
                child.consent_child_protection = row[23].value
            child.work_type = row[24].value
            child.disability_type = row[25].value.split(',') if row[25].value else []
            child.disability_note = row[26].value
            child.other_disability_note = row[27].value
            child.school_name = row[28].value
            if row[31].value:
                child.retention_support = row[31].value
            if row[32].value:
                child.formal_education_type = row[32].value
            if row[33].value:
                child.formal_education_shift = row[33].value
            if row[34].value:
                child.informal_education_type = row[34].value

            child.referred_school_first = row[36].value
            child.referred_school_second = row[37].value
            child.referred_school_alp = row[38].value
            child.referred_org_bln = row[39].value
            child.referred_org_ece = row[40].value
            child.referral_reason = row[42].value.split(',') if row[42].value else []
            child.referral_note = row[43].value
            child.formid_ind = row[54].value

            child.save()

        except Exception as ex:
            print("---------------")
            ctr += 1
            # print(row[0].value, row[1].value, row[2].value, row[3].value)
            print("error: ", ex.message)
            print("---------------")
            pass
    print(ctr)


def update_children_data():
    from .models import Child2
    wb = load_workbook(filename='BTS_Outreach_data_05022018_original_children.xlsx', read_only=True)
    ws = wb['IndividualInfo']

    for row in ws.rows:
        try:
            if row[0].value == 'FORMID' or not row[0].value:
                continue
            child = Child2.objects.get(
                formid_ind=row[54].value
            )
            child.sex = row[56].value if row[56].value else 'Male'
            child.calculated_age = row[45].value

            # child.last_edu_system = row[16].value
            # child.last_school_formal_year = row[18].value
            # child.last_education_year = row[19].value
            # child.last_public_school_location = row[20].value
            # child.last_informal_education = row[21].value
            # child.not_enrolled_reasons = row[22].value.split(',') if row[22].value else []
            # if row[23].value:
            #     child.consent_child_protection = row[23].value
            # child.work_type = row[24].value
            # child.disability_type = row[25].value.split(',') if row[25].value else []
            # child.disability_note = row[26].value
            # child.other_disability_note = row[27].value
            # child.school_name = row[28].value
            # if row[31].value:
            #     child.retention_support = row[31].value
            # if row[32].value:
            #     child.formal_education_type = row[32].value
            # if row[33].value:
            #     child.formal_education_shift = row[33].value
            # if row[34].value:
            #     child.informal_education_type = row[34].value
            #
            # child.referred_school_first = row[36].value
            # child.referred_school_second = row[37].value
            # child.referred_school_alp = row[38].value
            # child.referred_org_bln = row[39].value
            # child.referred_org_ece = row[40].value
            # child.referral_reason = row[42].value.split(',') if row[42].value else []
            # child.referral_note = row[43].value
            # child.formid_ind = row[54].value

            child.save()

        except Exception as ex:
            print("---------------")
            print("error: ", ex.message)
            print("---------------")
            pass


@app.task
def create_children_data():
    from .models import Child2
    wb = load_workbook(filename='BTS_Outreach_data_05022018_original_children.xlsx', read_only=True)
    ws = wb['IndividualInfo']
    ctr = 0

    ID_TYPES = {
        'None': 6,
        'UNHCR': 1,
        'Lebanese': 5,
        'Other': 5,
        'Syria': 3,
    }

    for row in ws.rows:
        try:
            if row[0].value == 'FORMID' or not row[0].value:
                continue
            child = Child2()

            child.form_id = row[0].value
            child.first_name = row[1].value if row[1].value else 'None'
            child.father_name = row[2].value if row[2].value else 'None'
            child.last_name = row[3].value if row[3].value else 'None'
            child.mother_fullname = row[4].value if row[4].value else 'None'

            # data['mother_nationality'] = NATIONALITIES[row[5].value] if row[5].value in NATIONALITIES else 6
            child.mother_nationality_id = row[5].value if row[5].value else 6

            child.birthday_year = row[6].value if row[6].value else '1990'
            child.birthday_month = row[7].value if row[7].value else '1'
            child.birthday_day = row[8].value if row[8].value else '1'
            child.nationality_id = row[9].value if row[9].value else 6

            child.id_type_id = ID_TYPES[row[10].value] if row[10].value in ID_TYPES else 6

            child.id_number = row[11].value if row[11].value else '000000'  # ID_Num
            if row[13].value:  # Case_Individual_Num
                child.id_number = row[13].value
            elif row[14].value:  # ID_Individual_Num
                child.id_number = row[14].value
            elif row[12].value:  # UNHCR_Case_Num
                child.id_number = row[12].value

            child.sex = row[56].value if row[56].value else 'Male'

            child.last_edu_system = row[16].value
            child.last_school_formal_year = row[18].value
            child.last_education_year = row[19].value
            child.last_public_school_location = row[20].value
            child.last_informal_education = row[21].value
            child.not_enrolled_reasons = row[22].value.split(',') if row[22].value else []
            if row[23].value:
                child.consent_child_protection = row[23].value
            child.work_type = row[24].value
            child.disability_type = row[25].value.split(',') if row[25].value else []
            child.disability_note = row[26].value
            child.other_disability_note = row[27].value
            child.school_name = row[28].value
            if row[31].value:
                child.retention_support = row[31].value
            if row[32].value:
                child.formal_education_type = row[32].value
            if row[33].value:
                child.formal_education_shift = row[33].value
            if row[34].value:
                child.informal_education_type = row[34].value

            child.referred_school_first = row[36].value
            child.referred_school_second = row[37].value
            child.referred_school_alp = row[38].value
            child.referred_org_bln = row[39].value
            child.referred_org_ece = row[40].value
            child.referral_reason = row[42].value.split(',') if row[42].value else []
            child.referral_note = row[43].value
            child.calculated_age = row[45].value
            child.formid_ind = row[54].value

            child.save()

        except Exception as ex:
            print("---------------")
            print("error: ", ex.message)
            print("---------------")
            pass


@app.task
def link_household_to_children():
    from .models import HouseHold, Child2

    households = HouseHold.objects.all()
    for hh in households:
        ctr = 0
        children = Child2.objects.filter(form_id=hh.form_id)
        for child in children:
            ctr += 1
            child.barcode_subset = '{}-{}'.format(hh.barcode_number, ctr)
            child.household = hh
            # print(child.id)
            child.save()


@app.task
def update_household_nationality():
    from .models import HouseHold, Child

    households = HouseHold.objects.all()
    for hh in households:
        child = Child.objects.filter(form_id=hh.form_id).first()
        if child.nationality:
            hh.nationality = child.nationality
            hh.save()


@app.task
def update_student_grade():
    from student_registration.students.models import CrossMatching

    children = CrossMatching.objects.filter(program_type='2nd-shift')
    for hh in children:
        student = hh.student
        enrollment = student.student_enrollment.filter(education_year__current_year=True).first()
        if enrollment:
            hh.education_level = enrollment.classroom_id
            hh.save()


class MyEncoder(json.JSONEncoder):

    def default(self, obj):
        if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)

    def decode(self, obj):
        if isinstance(obj, datetime.datetime):
            return int(mktime(obj.timetuple()))

        return json.JSONEncoder.default(self, obj)


def post_data(protocol, url, apifunc, token, data):

    params = json.dumps(data, cls=MyEncoder)

    headers = {"Content-type": "application/json", "Authorization": token, "HTTP_REFERER": url, "Cookie": "token="+token}

    if protocol == 'HTTPS':
        conn = httplib.HTTPSConnection(url)
    else:
        conn = httplib.HTTPConnection(url)
    conn.request('POST', apifunc, params, headers)
    response = conn.getresponse()
    result = response.read()

    if not response.status == 201:
        if response.status == 400:
            raise Exception(str(response.status) + response.reason + response.read())
        else:
            raise Exception(str(response.status) + response.reason)

    conn.close()

    return result


@app.task
def cross_matching_children(program_type='2nd-shift'):
    from .models import Child
    from student_registration.students.models import Student, CrossMatching
    from student_registration.schools.models import EducationYear
    from student_registration.alp.models import Outreach

    offset = 0
    limit = offset + 40000
    # children = Child.objects.all()[offset:limit]
    children = Child.objects.all()
    print(children.count())
    if program_type == 'ALP':
        students = Student.objects.filter(
            alp_enrollment__alp_round__in=[7, 9],
            alp_enrollment__registered_in_level__isnull=False
        )
    if program_type == '2nd-shift':
        education_year = EducationYear.objects.get(current_year=True)
        students = Student.objects.filter(student_enrollment__education_year=education_year)
    print(students.count())
    students = students.exclude(matched__isnull=False)
    print(students.count())

    for child in children:

        ##########################
        matched1 = students.filter(
            number=child.number
        ).first()
        if matched1:
            CrossMatching.objects.get_or_create(
                student=matched1,
                child=child,
                matched_on=child.number,
                pertinence=1,
                program_type=program_type
            )
            continue

        ##########################
        if child.id_number:
            matched2 = students.filter(
                id_number=child.id_number
            ).first()
            if matched2:
                CrossMatching.objects.get_or_create(
                    student=matched2,
                    child=child,
                    matched_on=child.id_number,
                    pertinence=2,
                    program_type=program_type
                )
                continue

        ##########################
        matched3 = students.filter(
            first_name=child.first_name,
            father_name=child.father_name,
            last_name=child.last_name,
            birthday_year=child.birthday_year,
            sex=child.sex
        ).first()

        if matched3:
            CrossMatching.objects.get_or_create(
                student=matched3,
                child=child,
                matched_on="fullname+birthday_year+sex",
                pertinence=3,
                program_type=program_type
            )
            continue

        ##########################
        matched4 = students.filter(
            first_name=child.first_name,
            last_name=child.father_name,
            mother_fullname=child.mother_fullname,
            birthday_year=child.birthday_year,
            sex=child.sex
        ).first()

        if matched4:
            CrossMatching.objects.get_or_create(
                student=matched4,
                child=child,
                matched_on="name+mother+birthday_year+sex",
                pertinence=4,
                program_type=program_type
            )
            continue

        ##########################
        matched5 = students.filter(
            first_name=child.first_name,
            last_name=child.father_name,
            birthday_year=child.birthday_year,
            birthday_month=child.birthday_month,
            sex=child.sex
        ).first()

        if matched5:
            CrossMatching.objects.get_or_create(
                student=matched5,
                child=child,
                matched_on="name+birthday_year+birthday_month+sex",
                pertinence=5,
                program_type=program_type
            )
            continue


@app.task
def cross_matching_children_2(program_type='CBECE'):
    from .models import Child
    from student_registration.students.models import Student, CrossMatching
    from student_registration.schools.models import EducationYear
    from student_registration.clm.models import BLN, CBECE

    offset = 0
    limit = offset + 40000
    # children = Child.objects.all()[offset:limit]
    children = Child.objects.all()
    print(children.count())
    if program_type == 'ALP':
        students = Student.objects.filter(
            alp_enrollment__alp_round__in=[7, 9],
            alp_enrollment__registered_in_level__isnull=False
        )
    if program_type == 'BLN':
        students = Student.objects.filter(
            bln_enrollment__round__in=[3, 4]
        )
    if program_type == 'CBECE':
        students = Student.objects.filter(
            cbece_enrollment__round__in=[3, 4]
        )
    if program_type == '2nd-shift':
        education_year = EducationYear.objects.get(current_year=True)
        students = Student.objects.filter(student_enrollment__education_year=education_year)
    print(students.count())
    students = students.exclude(matched__isnull=False)
    print(students.count())

    for student in students:

        ##########################
        matched1 = children.filter(
            number=student.number
        ).first()
        if matched1:
            CrossMatching.objects.get_or_create(
                child=matched1,
                student=student,
                matched_on=student.number,
                pertinence=1,
                program_type=program_type
            )
            continue

        ##########################
        # if student.id_number:
        #     matched2 = children.filter(
        #         id_number=student.id_number
        #     ).first()
        #     if matched2:
        #         CrossMatching.objects.get_or_create(
        #             child=matched2,
        #             student=student,
        #             matched_on=student.id_number,
        #             pertinence=2,
        #             program_type=program_type
        #         )
        #         continue

        ##########################
        matched3 = children.filter(
            first_name=student.first_name,
            father_name=student.father_name,
            last_name=student.last_name,
            birthday_year=student.birthday_year,
            sex=student.sex
        ).first()

        if matched3:
            CrossMatching.objects.get_or_create(
                child=matched3,
                student=student,
                matched_on="fullname+birthday_year+sex",
                pertinence=3,
                program_type=program_type
            )
            continue

        ##########################
        matched4 = children.filter(
            first_name=student.first_name,
            last_name=student.father_name,
            mother_fullname=student.mother_fullname,
            birthday_year=student.birthday_year,
            sex=student.sex
        ).first()

        if matched4:
            CrossMatching.objects.get_or_create(
                child=matched4,
                student=student,
                matched_on="name+mother+birthday_year+sex",
                pertinence=4,
                program_type=program_type
            )
            continue

        ##########################
        matched5 = children.filter(
            first_name=student.first_name,
            last_name=student.father_name,
            birthday_year=student.birthday_year,
            birthday_month=student.birthday_month,
            sex=student.sex
        ).first()

        if matched5:
            CrossMatching.objects.get_or_create(
                child=matched5,
                student=student,
                matched_on="name+birthday_year+birthday_month+sex",
                pertinence=5,
                program_type=program_type
            )
            continue


@app.task
def calculate_child_age():
    from .models import Child2

    children = Child2.objects.all()

    for child in children:
        child.calculated_age = child.calc_age()
        child.save()
