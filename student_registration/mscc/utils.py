

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
