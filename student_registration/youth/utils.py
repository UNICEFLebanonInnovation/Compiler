# -- coding: utf-8 --
from itertools import chain
import datetime

from django.db.models import Exists, OuterRef, Subquery
from import_export import resources, fields

from student_registration.outreach.models import OutreachChild
from student_registration.students.models import Student
from student_registration.youth.models import Registration

from .models import PopulationGroups, MasterProgram

from student_registration.locations.models import Location


def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if hasattr(value, 'id'):
                value = getattr(value, 'id')
            data[field_name] = value

    return data


def to_array_many_field(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            # Handle ManyToManyField by converting to list of IDs
            if hasattr(value, 'all'):
                data[field_name] = list(value.values_list('id', flat=True))
            # Handle ForeignKey by getting the ID
            elif hasattr(value, 'id'):
                value = getattr(value, 'id')
                data[field_name] = value
            # Handle simple fields (CharField, IntegerField, etc.)
            else:
                data[field_name] = value
    return data



# def to_array_many_field(fields, obj):
#     data = {}
#     for field_name in fields:
#         if hasattr(obj, field_name):
#             value = getattr(obj, field_name)
#             # Handle ManyToManyField by converting to list of IDs
#             if hasattr(value, 'all'):
#                 value = value.values_list('id', flat=True)
#             # Handle ForeignKey by getting the ID
#             elif hasattr(value, 'id'):
#                 value = value.id
#             data[field_name] = value
#     return data


def get_outreach_child(outreach_id):
    initial = {}
    instance = OutreachChild.objects.get(id=outreach_id)
    initial['child_outreach'] = instance.id
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
        initial['parent_sop_national_number'] = instance.outreach_caregiver.caregiver_personal_id
        initial['parent_sop_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
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
    initial['student_old'] = instance.id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.father_name
    initial['child_last_name'] = instance.last_name
    initial['child_mother_fullname'] = instance.mother_fullname
    initial['child_birthday_year'] = instance.birthday_year
    initial['child_birthday_month'] = instance.birthday_month
    initial['child_birthday_day'] = instance.birthday_day
    initial['child_gender'] = instance.sex
    initial['child_nationality'] = instance.nationality.id if instance.nationality else 0
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
    # initial['parent_sop_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_sop_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['sop_national_number'] = instance.child_personal_id
    # initial['sop_national_number_confirm'] = instance.child_personal_id
    # initial['parent_national_number'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['parent_national_number_confirm'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['national_number'] = instance.child_personal_id
    # initial['national_number_confirm'] = instance.child_personal_id

    return initial


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = (
            'id',
            # 'adolescent__id',
            # 'adolescent_outreach',
            # 'adolescent_old',
            'partner__name',
            'type',
            'center__name',
            'center__governorate__name',
            'center__caza__name',
            'center__cadaster__name',
            # 'adolescent__id',
            # 'adolescent__number',
            # 'adolescent__first_name',
            # 'adolescent__father_name',
            # 'adolescent__last_name',
            # 'adolescent__mother_fullname',
            # 'adolescent__gender',
            # 'adolescent__nationality__name',
            # 'adolescent__nationality_other',
            # 'adolescent__birthday_year',
            # 'adolescent__birthday_month',
            # 'adolescent__birthday_day',
            # 'adolescent__father_educational_level',
            # 'adolescent__mother_educational_level',
            # 'adolescent__first_phone_number',
            # 'adolescent__first_phone_number_confirm',
            # 'adolescent__second_phone_number',
            # 'adolescent__second_phone_number_confirm',
            # 'adolescent__main_caregiver',
            # 'adolescent__main_caregiver_other',
            # 'adolescent__caregiver_first_name',
            # 'adolescent__caregiver_middle_name',
            # 'adolescent__caregiver_last_name',
            # 'adolescent__caregiver_mother_name',
            # 'adolescent__main_caregiver_nationality__name',
            # 'adolescent__main_caregiver_nationality_other',
            # 'adolescent__id_type',
            # 'adolescent__case_number',
            # 'adolescent__case_number_confirm',
            # 'adolescent__parent_individual_case_number',
            # 'adolescent__parent_individual_case_number_confirm',
            # 'adolescent__individual_case_number',
            # 'adolescent__individual_case_number_confirm',
            # 'adolescent__recorded_number',
            # 'adolescent__recorded_number_confirm',
            # 'adolescent__parent_national_number',
            # 'adolescent__parent_national_number_confirm',
            # 'adolescent__national_number',
            # 'adolescent__national_number_confirm',
            # 'adolescent__parent_syrian_national_number',
            # 'adolescent__parent_syrian_national_number_confirm',
            # 'adolescent__syrian_national_number',
            # 'adolescent__syrian_national_number_confirm',
            # 'adolescent__parent_sop_national_number',
            # 'adolescent__parent_sop_national_number_confirm',
            # 'adolescent__sop_national_number',
            # 'adolescent__sop_national_number_confirm',
            # 'adolescent__parent_other_number',
            # 'adolescent__parent_other_number_confirm',
            # 'adolescent__other_number',
            # 'adolescent__other_number_confirm',
            'registration_date',
            'owner__username',
            'modified_by__username',
            'created',
            'modified',
        )
        export_order = fields


def load_dashboard_data(param, grouping):
    from django.db import connection

    cursor = connection.cursor()
    cursor.execute(
        "SELECT count(mr.id), "+grouping+" "
        "FROM public.youth_registration mr, public.child_child cc "
        "WHERE mr.child_id = cc.id "+param+" "
        "GROUP By "+grouping
    )

    rows = cursor.fetchall()
    return rows
