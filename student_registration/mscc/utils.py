# -- coding: utf-8 --
from itertools import chain
import logging

from datetime import datetime, date
from django.core.exceptions import ValidationError
from django.db.models import Exists, OuterRef, Subquery
from django import forms
from import_export import resources, fields

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
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild
from student_registration.mscc.models import Registration, EducationService, Referral

logger = logging.getLogger(__name__)



def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            value = getattr(obj, field_name)
            if hasattr(value, 'id'):
                value = getattr(value, 'id')
            data[field_name] = value

    return data


def generate_services(child_age, registry, user=None):
    try:
        from .models import ProvidedServices, Packages
        from student_registration.users.templatetags.custom_tags import has_group

        packages = Packages.objects.filter(type=registry.type, age=child_age)
        if user and has_group(user, 'MSCC_YOUTH'):
            packages = packages.filter(category="Youth")

        for package in packages.all():
            instance, created = ProvidedServices.objects.get_or_create(name=package.name,
                                                                       registration=registry,
                                                                       type=package.type,
                                                                       category=package.category)
            instance.save()
    except Exception as ex:
        return False


def regenerate_services(child_age, registry, user=None):
    from .templatetags.simple_tags import service_data
    from .models import ProvidedServices

    ProvidedServices.objects.filter(registration=registry).delete()
    generate_services(child_age, registry, user)
    service = service_data('EducationService', registry)
    if service:
        service.education_program = ""
        service.save()


def update_service(service_name, registry_id, service_id):
    from .models import ProvidedServices
    ProvidedServices.objects.filter(registration_id=registry_id,
                                    name=service_name).update(service_id=service_id,
                                                              completed=True,
                                                              completion_date=datetime.now())


def generate_education_history(registration_id, child_id, student_old_id):
    from .models import EducationHistory

    # 'BLN'
    bln_old_registrations = BLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bln_old_registrations = list(bln_old_registrations)

    for reg_id in bln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type = 'BLN',
                                                                   programme_id = reg_id)
        instance.save()

    # 'ABLN'
    abln_old_registrations = ABLN.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    abln_old_registrations = list(abln_old_registrations)

    for reg_id in abln_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='ABLN',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Bridging'
    bridging_old_registrations = Bridging.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    bridging_old_registrations = list(bridging_old_registrations)

    for reg_id in bridging_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='Bridging',
                                                                   programme_id=reg_id)
        instance.save()


    # 'RS'
    rs_old_registrations = RS.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    rs_old_registrations = list(rs_old_registrations)

    for reg_id in rs_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='RS',
                                                                   programme_id=reg_id)
        instance.save()

    # 'CBECE'
    cbece_old_registrations = CBECE.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    cbece_old_registrations = list(cbece_old_registrations)

    for reg_id in cbece_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='CBECE',
                                                                   programme_id=reg_id)
        instance.save()

    # 'Inclusion'
    inclusion_old_registrations = Inclusion.objects.filter(student_id=student_old_id).values_list('id', flat=True)
    inclusion_old_registrations = list(inclusion_old_registrations)

    for reg_id in inclusion_old_registrations:
        instance, created = EducationHistory.objects.get_or_create(registration_id=registration_id,
                                                                   child=child_id,
                                                                   student_old=student_old_id,
                                                                   programme_type='Inclusion',
                                                                   programme_id=reg_id)
        instance.save()


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
    if instance.working_status == 'yes':
        initial['have_labour'] = 'Yes - Full Day'
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


def create_attendance(data, center_id):
    from datetime import datetime
    round_id = data["round_id"]
    education_program = data["education_program"]
    class_section = data["class_section"]
    try:
        attendance, created = MSCCAttendance.objects.get_or_create(round_id=round_id, center_id=center_id,
                                                                   attendance_date=datetime.strptime(data["attendance_date"], '%m/%d/%Y'),
                                                                   education_program=education_program,
                                                                   class_section=class_section
                                                                   )
        attendance.day_off = data["attendance_day_off"]
        attendance.close_reason = data["close_reason"]
        attendance.save()

        for child in data['children_attendance']:
            attendance_child, created = MSCCAttendanceChild.objects.get_or_create(attendance_day=attendance,
                                                                                  child_id=child['child_id'],
                                                                                  registration_id=child['registration_id']
                                                                                  )
            attendance_child.attended = child['attended']
            attendance_child.absence_reason = child['absence_reason']
            attendance_child.absence_reason_other = child['absence_reason_other']
            attendance_child.save()
        return True
    except Exception as ex:
        logger.exception(ex)
        return False


def load_child_attendance(center_id, round_id, attendance_date, education_program, class_section):
    from datetime import datetime

    attendance = None

    if attendance_date is not None:
        attendance_date = datetime.strptime(attendance_date, '%m/%d/%Y')

        attendance = MSCCAttendance.objects.filter(center_id=center_id,
                                                   attendance_date=attendance_date,
                                                   education_program=education_program,
                                                   class_section=class_section,
                                                   round_id=round_id
                                                   ).last()

    result = []

    try:
        if attendance:
            attendances = MSCCAttendanceChild.objects.filter(attendance_day=attendance)

            for attendance in attendances:
                attendance_record = {}
                attendance_record['registration_id'] = attendance.registration.id
                attendance_record['child_id'] = attendance.child.id
                attendance_record['child_fullname'] = attendance.child.full_name
                attendance_record['child_mother_fullname'] = attendance.child.mother_fullname
                attendance_record['child_birthday'] = attendance.child.birthday
                attendance_record['child_nationality'] = attendance.child.nationality.name
                attendance_record['attended'] = attendance.attended
                attendance_record['absence_reason'] = attendance.absence_reason
                attendance_record['absence_reason_other'] = attendance.absence_reason_other

                result.append(attendance_record)
        else:
            registrations = Registration.objects.filter(
                center_id=center_id,
                type='Core-Package',
                deleted=False,
                round_id=round_id
            ).annotate(
                has_education_service=Exists(
                    EducationService.objects.filter(
                        registration_id=OuterRef('pk'),
                        education_program=education_program,
                        class_section=class_section
                    )
                )
            ).filter(has_education_service=True)\
                .exclude(
                id__in=Subquery(
                    Referral.objects.filter(
                        registration_id=OuterRef('pk'),
                        recommended_learning_path='Drop out',
                        dropout_date__lte = attendance_date
                    ).values('registration_id')
                )
            )
            # print(registrations.query)
            for registration_child in registrations:
                registration_record = {}
                registration_record['registration_id'] = registration_child.id
                registration_record['child_id'] = registration_child.child.id
                registration_record['child_fullname'] = registration_child.child.full_name
                registration_record['child_mother_fullname'] = registration_child.child.mother_fullname
                registration_record['child_birthday'] = registration_child.child.birthday
                registration_record['child_nationality'] = registration_child.child.nationality.name
                registration_record['attended'] = 'Yes'
                registration_record['absence_reason'] = ''
                registration_record['absence_reason_other'] = ''
                result.append(registration_record)

        return result

    except Exception as ex:
        logger.exception(ex)
        return []


def update_child_attendance(registration_id, education_program, old_class_section, new_class_section):

    child_attendances = None

    child_attendances = MSCCAttendanceChild.objects.filter(registration_id=registration_id,
                                                           attendance_day__education_program=education_program,
                                                           attendance_day__class_section=old_class_section)

    try:
        if child_attendances:
            for ca in child_attendances:
                center_id = ca.attendance_day.center.id
                attendance_date = ca.attendance_day.attendance_date

                # Search if attendance for the new class exists and move the child attendance to it
                new_attendance = MSCCAttendance.objects.filter(center_id=center_id,
                                                           attendance_date=attendance_date,
                                                           education_program=education_program,
                                                           class_section=new_class_section
                                                           ).last()
                attendance_id = ca.attendance_day.id

                # Count the number of other attendances for the same day
                other_children_count = MSCCAttendanceChild.objects.filter(attendance_day=ca.attendance_day).exclude(id=ca.id).count()

                if new_attendance:
                    ca.attendance_day = new_attendance
                    ca.save()
                else:
                    ca.delete()

                if other_children_count == 0:
                    try:
                        old_attendance = MSCCAttendance.objects.get(id=attendance_id)

                        # Delete the unique old_attendance instance
                        old_attendance.delete()

                    except MSCCAttendance.DoesNotExist:
                        logger.warning("Old attendance does not exist.")


    except Exception as ex:
        logger.exception(ex)
        return []


class RegistrationResource(resources.ModelResource):
    class Meta:
        model = Registration
        fields = (
            'id',
            'child__id',
            'child_outreach',
            'student_old',
            'partner__name',
            'type',
            'center__name',
            'center__governorate__name',
            'center__caza__name',
            'center__cadaster__name',
            'child__id',
            'child__number',
            'child__first_name',
            'child__father_name',
            'child__last_name',
            'child__mother_fullname',
            'child__gender',
            'child__nationality__name',
            'child__nationality_other',
            'child__birthday_year',
            'child__birthday_month',
            'child__birthday_day',
            'child__p_code',
            'child__address',
            'child__disability',
            'child__marital_status',
            'child__have_children',
            'child__children_number',
            'source_of_identification',
            'source_of_identification_specify',
            'cash_support_programmes',
            'child__father_educational_level',
            'child__mother_educational_level',
            'child__first_phone_owner',
            'child__first_phone_number',
            'child__first_phone_number_confirm',
            'child__second_phone_owner',
            'child__second_phone_number',
            'child__second_phone_number_confirm',
            'child__main_caregiver',
            'child__main_caregiver_other',
            'child__caregiver_first_name',
            'child__caregiver_middle_name',
            'child__caregiver_last_name',
            'child__caregiver_mother_name',
            'child__main_caregiver_nationality__name',
            'child__main_caregiver_nationality_other',
            'have_labour',
            'labour_type',
            'labour_type_specify',
            'labour_hours',
            'labour_weekly_income',
            'child__id_type',
            'child__case_number',
            'child__case_number_confirm',
            'child__parent_individual_case_number',
            'child__parent_individual_case_number_confirm',
            'child__individual_case_number',
            'child__individual_case_number_confirm',
            'child__recorded_number',
            'child__recorded_number_confirm',
            'child__parent_national_number',
            'child__parent_national_number_confirm',
            'child__national_number',
            'child__national_number_confirm',
            'child__parent_syrian_national_number',
            'child__parent_syrian_national_number_confirm',
            'child__syrian_national_number',
            'child__syrian_national_number_confirm',
            'child__parent_sop_national_number',
            'child__parent_sop_national_number_confirm',
            'child__sop_national_number',
            'child__sop_national_number_confirm',
            'child__parent_other_number',
            'child__parent_other_number_confirm',
            'child__other_number',
            'child__other_number_confirm',
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
        "FROM public.mscc_registration mr, public.child_child cc "
        "WHERE mr.child_id = cc.id "+param+" "
        "GROUP By "+grouping
    )

    rows = cursor.fetchall()
    return rows


class TrimmedDateField(forms.DateField):
    """DateField that strips whitespace before parsing."""

    def to_python(self, value):
        if hasattr(value, 'strip'):
            value = value.strip()
        return super().to_python(value)


def validate_date(date_str):

    if not date_str:
        return None

    # If the value is already a date object, return it as is
    if isinstance(date_str, date):
        return date_str

    # Trim white spaces from the provided value
    if hasattr(date_str, 'strip'):
        date_str = date_str.strip()

    # Supported date format
    formats = ['%Y-%m-%d']
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt).date()
        except ValueError:
            continue

    raise ValidationError("Date is not valid. Please use the format YYYY-MM-DD.")


