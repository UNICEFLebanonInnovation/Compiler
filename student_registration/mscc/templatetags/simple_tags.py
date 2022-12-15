from django import template
from django.apps import apps

register = template.Library()


@register.simple_tag
def have_service(services, service_name):
    return services.filter(name=service_name).exists()


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
    model = apps.get_model('mscc', model_name)
    return model.objects.filter(registration=obj).last()
