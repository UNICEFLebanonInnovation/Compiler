from django import template
from django.apps import apps

from student_registration.youth.models import   Registration, Round


register = template.Library()


@register.simple_tag
def have_service(services, service_name):
    if service_name in services:
        return services[service_name]


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
def get_child_fullname(registry):
    reg = Registration.objects.filter(id=registry).last()
    return reg.child_fullname



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



