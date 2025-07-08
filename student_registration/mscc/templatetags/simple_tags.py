from django import template
from django.apps import apps
import logging

from student_registration.mscc.models import ProvidedServices, EducationHistory, Registration, EducationService, Round, Packages
from student_registration.attendances.models import MSCCAttendance, MSCCAttendanceChild


register = template.Library()
logger = logging.getLogger(__name__)


@register.simple_tag
def have_service(services, service_name):
    if service_name in services:
        return services[service_name]


@register.simple_tag
def get_service_info(services, registry, service_name):
    return services.filter(name=service_name, registration=registry).last()


@register.simple_tag
def get_child_fullname(registry):
    reg = Registration.objects.filter(id=registry).last()
    return reg.child_fullname


@register.simple_tag
def get_regitration_type(registry):
    reg = Registration.objects.filter(id=registry).last()
    return reg.type


@register.simple_tag
def get_child_rounds(registry):
    from django.db.models import Subquery
    registration_ids = Registration.objects.filter(
        child_id=Subquery(
            Registration.objects.filter(id=registry).values('child_id')[:1]
        )
    ).values_list('id', flat=True)
    round_names = Round.objects.filter(
        id__in=EducationService.objects.filter
        (registration_id__in=registration_ids,
         registration__deleted=False).values_list('round_id',flat=True)).values_list('name', flat=True).distinct()

    if round_names:
        return round_names
    else:
        return None

@register.simple_tag
def get_service(registry, service_name):
    if type(registry) == 'int':
        return ProvidedServices.objects.filter(name=service_name, registration_id=registry).last()
    return ProvidedServices.objects.filter(name=service_name, registration=registry).last()

@register.simple_tag
def get_youth_services(registry,service_name):
    if type(registry) == 'int':
        return Packages.objects.filter(type=registry.type, age=registry.child_age).last()
    return Packages.objects.filter(type=registry.type, age=registry.child_age).last()


@register.simple_tag
def get_education_service(registry):
    if type(registry) == 'int':
        education_service = EducationService.objects.filter(registration_id=registry).last()
    education_service = EducationService.objects.filter( registration=registry).last()
    if education_service:
        return education_service.education_program
    else:
        return None


@register.simple_tag
def get_service_all(registry, model_name):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=registry)
    except Exception as ex:
        return False


@register.simple_tag
def get_education_service_history(child_id):
    try:
        return EducationService.objects.filter( registration__child_id=child_id,registration__deleted=False)\
            .order_by('registration_date')

    except Exception as ex:
        return False


@register.simple_tag
def get_services(registry):
    return ProvidedServices.objects.filter(registration=registry)


@register.simple_tag
def get_completion_rate(registry):
    services = get_services(registry)
    nbr_services = services.count()
    nbr_completed = services.filter(completed=True).count()
    try:
        return int(round(float(nbr_completed)/float(nbr_services), 2) * 100.0)
    except Exception as ex:
        return 0


@register.simple_tag
def service_completed(services, service_name):
    return services.filter(name=service_name, completed=True).exists()


@register.simple_tag
def service_required(services, service_name):
    return services.filter(name=service_name, required=True).exists()


@register.simple_tag
def service_info(services, service_name):
    return services.filter(name=service_name)


@register.simple_tag
def have_service_category(category, obj):
    try:
        services = get_services(obj)
        return services.filter(category=category).count()
    except Exception as ex:
        return False


@register.simple_tag
def have_education_programme(programme_type):
    try:
        programmes = ['BLN Level 1', 'BLN Level 2', 'BLN Level 3','BLN Catch-up' ,'ABLN Level 1', 'ABLN Level 2',
                      'ABLN Catch-up', 'CBECE Level 1', 'CBECE Level 2', 'CBECE Level 3', 'RS Grade 1', 'RS Grade 2',
                      'RS Grade 3', 'RS Grade 4', 'RS Grade 5', 'RS Grade 6', 'RS Grade 7', 'RS Grade 8', 'RS Grade 9',
                      'YFS Level 1 - RS Grade 9', 'YFS Level 2 - RS Grade 9']
        if programme_type in programmes:
            return True
    except Exception as ex:
        return False


@register.simple_tag
def have_youth_programme(programme_type):
    try:
        programmes = ['YBLN Level 1', 'YBLN Level 2','YBLN Catch-up',
                      'YFS Level 1', 'YFS Level 2',
                      'YFS Level 1 - RS Grade 9', 'YFS Level 2 - RS Grade 9']
        if programme_type in programmes:
            return True
    except Exception as ex:
        return False


@register.simple_tag
def service_data(model_name, obj):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=obj).last()
    except Exception as ex:
        return False

@register.simple_tag
def service_youth_data(model_name, obj, service_type):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=obj, service_type=service_type).last()
    except Exception as ex:
        return False

@register.simple_tag
def education_history(registration_id):
    return EducationHistory.objects.filter(registration_id=registration_id)


@register.simple_tag
def education_history_programmes(student_id):
    try:
        programmes = []
        programme_types = ['BLN', 'ABLN', 'Bridging', 'RS', 'CBECE', 'Inclusion']

        for programme_type in programme_types:
            if education_history_programme(programme_type, student_id):
                programmes.append(programme_type)

        return ", ".join(programmes)
    except Exception as ex:
        return ''


def education_history_programme(model_name, student_id):
    try:
        model = apps.get_model('clm', model_name)
        e = model.objects.filter(student_id=student_id).exists()
        return e
    except Exception as ex:
        return False


@register.simple_tag
def education_history_model(programme_id, programme_type):
    try:
        model = apps.get_model('clm', programme_type)
        model_data = model.objects.get(id=programme_id)
        return model_data
    except Exception as ex:
        return None


@register.simple_tag
def get_educations_data(obj):
    try:
        history = education_history(obj)

        educations = []
        for item in history:
            model = apps.get_model('clm', item.programme_type)
            model_data = model.objects.get(id=item.programme_id)
            educations.append({
                'programme_type': item.programme_type,
                'programme_id': item.programme_id,
                'round': model_data.round,
                'registration_level': model_data.registration_level,
                'center': model_data.center,
                'registration_date': model_data.registration_date
            })
        return educations
    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def child_attendance(child_id):
    try:
        return MSCCAttendanceChild.objects.filter(child_id=child_id)

    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def child_attendance_history(child_id):
    try:
        details = {}
        from datetime import datetime
        today = datetime.today()

        attendances = MSCCAttendanceChild.objects.filter(child_id=child_id)

        details['ttl_days'] = attendances.count()
        details['ttl_attended'] = attendances.filter(attended='Yes').count()
        details['ttl_absence'] = attendances.filter(attended='No').count()
        details['ttl_absence_month'] = attendances.filter(attended='No',
                                                          attendance_day__attendance_date__month=today.month).count()
        details['ttl_off'] = 0

        return details
    except Exception as ex:
        logger.exception(ex)
        return []


@register.simple_tag
def eligible_to_followup(registry):

    try:
        disability = True if registry.child.disability else False
        if disability:
            return True

        referral = service_data('Referral', register)
        if referral and referral.referred_service == 'CP':
            return True

        if get_service(registry, 'PSS'):
            return True

        return False
    except Exception as ex:
        return False


@register.simple_tag
def grading_improvement(instance, field):
    if not instance:
        return 0
    if not instance.pre_test or not instance.post_test:
        return 0
    pre_value = instance.pre_test[field] if field in instance.pre_test else 0
    post_value = instance.post_test[field] if field in instance.post_test else 0
    if pre_value and post_value:
        try:
            return '{}{}'.format(
                round(((float(post_value) - float(pre_value)) /
                       float(pre_value)) * 100.0, 2), '%')
        except ZeroDivisionError:
            return 0.0
    return 0.0
