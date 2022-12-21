# -- coding: utf-8 --

import datetime

from student_registration.outreach.models import OutreachChild

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
        ProvidedServices.objects.create(name=package.name, registration=registry, type=package.type)
        ProvidedServices.save()


def update_service(service_name, registry_id, service_id):
    from .models import ProvidedServices
    ProvidedServices.objects.filter(registration_id=registry_id,
                                    name=service_name).update(service_id=service_id,
                                                              completed=True,
                                                              completion_date=datetime.datetime.now())


def get_outreach_child(initial,outreach_id,center_id):
    from datetime import datetime
    instance = OutreachChild.objects.get(id=outreach_id)
    initial['center'] = center_id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.outreach_caregiver.father_name
    initial['child_last_name'] = instance.outreach_caregiver.last_name
    initial['child_mother_fullname'] = instance.outreach_caregiver.mother_full_name
    if instance.date_of_birth :
        dt_string = instance.date_of_birth
        dt = datetime.strptime(dt_string, '%Y-%m-%d')
        initial['child_birthday_year'] = dt.year
        initial['child_birthday_month'] = dt.month
        initial['child_birthday_day'] = dt.day
    initial['gender'] = instance.gender
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
