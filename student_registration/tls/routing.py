from django.urls import reverse


def module_namespace(request):
    match = getattr(request, 'resolver_match', None)
    return 'sdc' if match and match.namespace == 'sdc' else 'tls'


def reverse_module(request, name, **kwargs):
    return reverse(f'{module_namespace(request)}:{name}', **kwargs)
