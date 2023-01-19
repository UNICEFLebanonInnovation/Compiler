# -- coding: utf-8 --
from itertools import chain
import datetime


from student_registration.outreach.models import OutreachChild
from student_registration.students.models import Student
from student_registration.clm.models import (
    BLN,
    ABLN,
    Bridging,
    RS,
    CBECE,
    Inclusion
)

def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            data[field_name] = getattr(obj, field_name)

    return data


def generate_services(child_age, registry):
    from .models import ProvidedServices, Packages

    packages = Packages.objects.filter(type=registry.type, age=child_age)

    for package in packages.all():
        instance, created = ProvidedServices.objects.get_or_create(name=package.name,
                                                                   registration=registry,
                                                                   type=package.type)
        instance.save()


def update_service(service_name, registry_id, service_id):
    from .models import ProvidedServices
    ProvidedServices.objects.filter(registration_id=registry_id,
                                    name=service_name).update(service_id=service_id,
                                                              completed=True,
                                                              completion_date=datetime.datetime.now())


def generate_education_history(registration_id, child_id, student_old_id):
    from .models import EducationHistory

    # 'BLN'
    bln_old_registrations = BLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bln_old_registrations = list(bln_old_registrations)

    for reg_id in bln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child_id=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type = 'BLN',
                                                                   programme_id = reg_id)
        instance.save()

    # 'ABLN'
    abln_old_registrations = ABLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    abln_old_registrations = list(abln_old_registrations)

    for reg_id in abln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type='ABLN',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Bridging'
    bridging_old_registrations = Bridging.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bridging_old_registrations = list(bridging_old_registrations)

    for reg_id in bridging_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type='Bridging',
                                                                   programme_id=reg_id)
        instance.save()


    # 'RS'
    rs_old_registrations = RS.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    rs_old_registrations = list(rs_old_registrations)

    for reg_id in rs_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type='RS',
                                                                   programme_id=reg_id)
        instance.save()

    # 'CBECE'
    cbece_old_registrations = CBECE.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    cbece_old_registrations = list(cbece_old_registrations)

    for reg_id in cbece_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type='CBECE',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Inclusion'
    inclusion_old_registrations = Inclusion.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    inclusion_old_registrations = list(inclusion_old_registrations)

    for reg_id in inclusion_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old_id=student_old_id,
                                                                   programme_type='Inclusion',
                                                                   programme_id=reg_id)
        instance.save()


def get_outreach_child(outreach_id):
    initial = {}
    instance = OutreachChild.objects.get(id=outreach_id)
    initial['child_outreach_id'] = instance.id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.outreach_caregiver.father_name
    initial['child_last_name'] = instance.outreach_caregiver.last_name
    initial['child_mother_fullname'] = instance.outreach_caregiver.mother_full_name
    initial['child_birthday_year'] = instance.birthday_year
    initial['child_birthday_month'] = instance.birthday_month
    initial['child_birthday_day'] = instance.birthday_day
    initial['child_gender'] = instance.gender
    nationality = instance.nationality
    if nationality == 'syrian':
        initial['child_nationality'] = 1
    elif nationality == 'lebanese':
        initial['child_nationality'] = 5
    elif nationality == 'palestinian':
        initial['child_nationality'] = 4
    elif nationality == 'iraqi':
        initial['child_nationality'] = 2
    elif nationality == 'stateless':
        initial['child_nationality'] = 7
    elif nationality == 'other':
        initial['child_nationality'] = 6
    initial['child_nationality_other'] = instance.nationality_other
    initial['child_address'] = instance.outreach_caregiver.address

    disability = instance.disability
    if disability == 'no':
        initial['child_disability'] = 1
    elif disability == 'difficulty_seeing':
        initial['child_disability'] = 6
    elif disability == 'difficulty_interacting_with_others':
        initial['child_disability'] = 9
    elif disability == 'difficulty_speaking':
        initial['child_disability'] = 5
    elif disability == 'intellectual_disability':
        initial['child_disability'] = 10
    elif disability == 'difficulty_hearing':
        initial['child_disability'] = 3
    elif disability == 'learning_difficulties':
        initial['child_disability'] = 8
    elif disability == 'difficulty_walking_or_moving_hands':
        initial['child_disability'] = 4
    elif disability == 'Other':
        initial['child_disability'] = 2
    initial['disability_other'] = instance.disability_other
    initial['child_marital_status'] = instance.family_status.capitalize()

    main_caregiver_nationality = instance.outreach_caregiver.caregiver_nationality
    if main_caregiver_nationality == 'syrian':
        initial['main_caregiver_nationality'] = 1
    elif main_caregiver_nationality == 'lebanese':
        initial['main_caregiver_nationality'] = 5
    elif main_caregiver_nationality == 'palestinian':
        initial['main_caregiver_nationality'] = 4
    elif main_caregiver_nationality == 'iraqi':
        initial['main_caregiver_nationality'] = 2
    elif main_caregiver_nationality == 'stateless':
        initial['main_caregiver_nationality'] = 7
    elif main_caregiver_nationality == 'other':
        initial['main_caregiver_nationality'] = 6
    initial['main_caregiver_nationality_other'] = instance.outreach_caregiver.caregiver_nationality_other

    initial['have_labour'] = instance.working_status.capitalize()
    labour_type = instance.work_type
    if labour_type == 'manufacturing_producing':
        initial['labour_type'] = 'Manufacturing'
    elif labour_type == 'garage_mechanics_workshop':
        initial['labour_type'] = ''
    elif labour_type == 'construction_site':
        initial['labour_type'] = 'Building'
    elif labour_type == 'shop_restaurant_bakery_barber':
        initial['labour_type'] = 'Retail / Store'
    elif labour_type == 'street_connected_work__begging__vending_':
        initial['labour_type'] = 'Begging'
    elif labour_type == 'agriculture_animal_herding':
        initial['labour_type'] = 'Agriculture'
    elif labour_type == 'others':
        initial['labour_type'] = 'Other services'
    else:
        initial['labour_type'] = ''

    initial['labour_type_specify'] = instance.work_type_other
    initial['first_phone_number'] = instance.outreach_caregiver.primary_phone
    initial['first_phone_number_confirm'] = instance.outreach_caregiver.primary_phone
    initial['second_phone_number'] = instance.outreach_caregiver.secondary_phone
    initial['second_phone_number_confirm'] = instance.outreach_caregiver.secondary_phone

    main_caregiver = instance.outreach_caregiver.main_caregiver
    if main_caregiver == u'الاب':
        initial['main_caregiver'] = 'Father'
        initial['caregiver_first_name'] = instance.outreach_caregiver.father_name
        initial['caregiver_last_name'] = instance.outreach_caregiver.last_name
    else:
        if main_caregiver == u'الام':
            initial['main_caregiver'] = 'Mother'
        elif main_caregiver == u'اخر':
            initial['main_caregiver'] = 'Other'
        initial['caregiver_first_name'] = instance.outreach_caregiver.caregiver_first_name
        initial['caregiver_last_name'] = instance.outreach_caregiver.caregiver_last_name

    initial['caregiver_middle_name'] = instance.outreach_caregiver.caregiver_father_name
    initial['caregiver_mother_name'] = instance.outreach_caregiver.caregiver_mother_name

    id_type = instance.outreach_caregiver.id_type
    if id_type == 'unhcr_registered':
        initial['id_type'] = 1
        initial['case_number'] = instance.outreach_caregiver.unhcr_case_number
        initial['case_number_confirm'] = instance.outreach_caregiver.unhcr_case_number
        initial['parent_individual_case_number'] = instance.outreach_caregiver.caregiver_unhcr_id
        initial['parent_individual_case_number_confirm'] = instance.outreach_caregiver.caregiver_unhcr_id
        initial['individual_case_number'] = instance.child_unhcr_number
        initial['individual_case_number_confirm'] = instance.child_unhcr_number
    elif id_type == 'unhcr_recorded':
        initial['id_type'] = 2
        initial['recorded_number'] = instance.outreach_caregiver.unhcr_barcode
        initial['recorded_number_confirm'] = instance.outreach_caregiver.unhcr_barcode
    elif id_type == 'syrian_id':
        initial['id_type'] = 3
        initial['parent_syrian_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_syrian_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['syrian_national_number'] = instance.child_personal_id
        initial['syrian_national_number_confirm'] = instance.child_personal_id
    elif id_type == 'palestinian_id':
        initial['id_type'] = 4
        initial['sop_parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['sop_parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['sop_national_number'] = instance.child_personal_id
        initial['sop_national_number_confirm'] = instance.child_personal_id
    elif id_type == 'lebanese_id':
        initial['id_type'] = 5
        initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
        initial['national_number'] = instance.child_personal_id
        initial['national_number_confirm'] = instance.child_personal_id

    return initial


def get_old_child(student_id):
    initial = {}
    instance = Student.objects.get(id=student_id)
    initial['student_old_id'] = instance.id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.father_name
    initial['child_last_name'] = instance.last_name
    initial['child_mother_full_name'] = instance.mother_fullname
    initial['child_birthday_year'] = instance.birthday_year
    initial['child_birthday_month'] = instance.birthday_month
    initial['child_birthday_day'] = instance.birthday_day
    initial['child_gender'] = instance.sex
    initial['child_nationality'] = instance.nationality.id
    initial['child_marital_status'] = instance.family_status

    # initial['id_type'] = instance.outreach_caregiver.id_type
    # initial['case_number'] = instance.outreach_caregiver.unhcr_case_number
    # initial['case_number_confirm'] = instance.outreach_caregiver.unhcr_case_number
    # initial['parent_individual_case_number'] = instance.outreach_caregiver.caregiver_unhcr_id
    # initial['parent_individual_case_number_confirm'] = instance.outreach_caregiver.caregiver_unhcr_id
    # initial['individual_case_number'] = instance.child_unhcr_number
    # initial['individual_case_number_confirm'] = instance.child_unhcr_number
    # initial['recorded_number'] = instance.outreach_caregiver.unhcr_barcode
    # initial['recorded_number_confirm'] = instance.outreach_caregiver.unhcr_barcode
    # initial['parent_syrian_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_syrian_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['syrian_national_number'] = instance.child_personal_id
    # initial['syrian_national_number_confirm'] = instance.child_personal_id
    # initial['sop_parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['sop_parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['sop_national_number'] = instance.child_personal_id
    # initial['sop_national_number_confirm'] = instance.child_personal_id
    # initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['national_number'] = instance.child_personal_id
    # initial['national_number_confirm'] = instance.child_personal_id

    return initial

