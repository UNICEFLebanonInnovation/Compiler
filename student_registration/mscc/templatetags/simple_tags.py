from django import template
from django.apps import apps

from student_registration.mscc.models import ProvidedServices, EducationHistory

register = template.Library()


@register.simple_tag
def have_service(services, service_name):
    if service_name in services:
        return services[service_name]


@register.simple_tag
def get_service_info(services, registry, service_name):
    return services.filter(name=service_name, registration=registry).last()


@register.simple_tag
def get_service(registry, service_name):
    if type(registry) == 'int':
        return ProvidedServices.objects.filter(name=service_name, registration_id=registry).last()
    return ProvidedServices.objects.filter(name=service_name, registration=registry).last()


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
def service_data(model_name, obj):
    try:
        model = apps.get_model('mscc', model_name)
        return model.objects.filter(registration=obj).last()
    except Exception as ex:
        return False


@register.simple_tag
def education_history(registration_id):
    return EducationHistory.objects.filter(registration_id=registration_id)


@register.simple_tag
def get_educations_data(obj):
    try:
        history = education_history(obj)
        print(history.count())
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
        print(ex.message)
        return []
