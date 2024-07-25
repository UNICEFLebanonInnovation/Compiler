from django import template
from django.apps import apps

from student_registration.youth.models import   Registration, Round, EnrolledPrograms, YouthAssessment


register = template.Library()

@register.simple_tag(name='youth_simple_tag')
def youth_simple_tag():
    return "Youth Tag"


@register.simple_tag
def have_service(services, service_name):
    if service_name in services:
        return services[service_name]

@register.simple_tag
def get_enrolled_program(registry):
    if type(registry) == 'int':
        enrolled_programs = EnrolledPrograms.objects.filter(registration_id=registry).last()
    enrolled_programs = EnrolledPrograms.objects.filter( registration=registry).last()
    if enrolled_programs:
        return enrolled_programs.master_program
    else:
        return None

@register.simple_tag
def get_service(registry, service_name):
    return None
    # if type(registry) == 'int':
    #     return ProvidedServices.objects.filter(name=service_name, registration_id=registry).last()
    # return ProvidedServices.objects.filter(name=service_name, registration=registry).last()

@register.simple_tag
def have_youth_programme(programme_type):
    return False
    # try:
    #     programmes = ['YBLN Level 1', 'YBLN Level 2', 'YFS Level 1', 'YFS Level 2']
    #     if programme_type in programmes:
    #         return True
    # except Exception as ex:
    #     return False


@register.simple_tag
def grading_improvement(instance, field):
    return 0.0
    # if not instance:
    #     return 0
    # if not instance.pre_test or not instance.post_test:
    #     return 0
    # pre_value = instance.pre_test[field] if field in instance.pre_test else 0
    # post_value = instance.post_test[field] if field in instance.post_test else 0
    # if pre_value and post_value:
    #     try:
    #         return '{}{}'.format(
    #             round(((float(post_value) - float(pre_value)) /
    #                    float(pre_value)) * 100.0, 2), '%')
    #     except ZeroDivisionError:
    #         return 0.0
    # return 0.0


@register.simple_tag
def have_service_category(category, obj):
    return False
    # try:
    #     services = get_services(obj)
    #     return services.filter(category=category).count()
    # except Exception as ex:
    #     return False
    #

@register.simple_tag
def have_education_programme(programme_type):
    return False
    # try:
    #     programmes = ['BLN Level 1', 'BLN Level 2', 'BLN Level 3', 'ABLN Level 1', 'ABLN Level 2',
    #                   'CBECE Level 1', 'CBECE Level 2', 'CBECE Level 3', 'RS Grade 7', 'RS Grade 8', 'RS Grade 9']
    #     if programme_type in programmes:
    #         return True
    # except Exception as ex:
    #     return False

@register.simple_tag
def get_service_info(services, registry, service_name):
    return "123"

@register.simple_tag
def get_services(registry):
    return "123"

@register.simple_tag
def get_completion_rate(registry):
    return 0
    # services = get_services(registry)
    # nbr_services = services.count()
    # nbr_completed = services.filter(completed=True).count()
    # try:
    #     return int(round(float(nbr_completed)/float(nbr_services), 2) * 100.0)
    # except Exception as ex:
    #     return 0

@register.simple_tag
def get_youth_services(registry,service_name):
    return None
    # if type(registry) == 'int':
    #     return Packages.objects.filter(type=registry.type, age=registry.child_age).last()
    # return Packages.objects.filter(type=registry.type, age=registry.child_age).last()

@register.simple_tag
def service_youth_data(model_name, obj, service_type):
    return False
    # try:
    #     model = apps.get_model('mscc', model_name)
    #     return model.objects.filter(registration=obj, service_type=service_type).last()
    # except Exception as ex:
    #     return False


@register.simple_tag
def get_service_all(registry, model_name):
    return False
    # try:
    #     model = apps.get_model('mscc', model_name)
    #     return model.objects.filter(registration=registry)
    # except Exception as ex:
    #     return False


@register.simple_tag
def eligible_to_followup(registry):
    return False

    # try:
    #     disability = True if registry.child.disability else False
    #     if disability:
    #         return True
    #
    #     referral = service_data('Referral', register)
    #     if referral and referral.referred_service == 'CP':
    #         return True
    #
    #     if get_service(registry, 'PSS'):
    #         return True
    #
    #     return False
    # except Exception as ex:
    #     return False

@register.simple_tag
def get_child_fullname(registry):
    reg = Registration.objects.filter(id=registry).last()
    return reg.adolescent_fullname



@register.simple_tag
def service_completed(services, service_name):
    return services.filter(name=service_name, completed=True).exists()


@register.simple_tag
def service_required(services, service_name):
    return services.filter(name=service_name, required=True).exists()


@register.simple_tag
def service_data(model_name, obj):
    try:
        model = apps.get_model('youth', model_name)
        return model.objects.filter(registration=obj).last()
    except Exception as ex:
        return False

@register.simple_tag
def program_data(model_name, obj):
    try:
        model = apps.get_model('youth', model_name)
        return model.objects.filter(registration=obj)
    except Exception as ex:
        return False




