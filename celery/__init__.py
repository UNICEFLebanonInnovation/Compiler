"""Stub Celery application used in tests."""


class Celery:
    def __init__(self, name):
        self.name = name
        self.conf = type('Conf', (), {'task_default_queue': name})()

    def config_from_object(self, config):  # pragma: no cover - compatibility
        return None

    def autodiscover_tasks(self, packages):  # pragma: no cover - compatibility
        return packages

    def task(self, *args, **kwargs):  # noqa: D401 - mimic Celery decorator
        def decorator(func):
            return func

        if args and callable(args[0]):
            return args[0]
        return decorator


class CeleryConfig:
    broker_url = 'memory://'
    result_backend = 'memory://'
