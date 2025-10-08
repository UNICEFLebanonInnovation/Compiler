"""Stub DRF serializers."""


class ValidationError(Exception):
    pass


class Field:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


class CharField(Field):
    pass


class BooleanField(Field):
    pass


class DateField(Field):
    pass


class IntegerField(Field):
    pass


class JSONField(Field):
    pass


class Serializer:
    def __init__(self, *args, **kwargs):  # pragma: no cover - compatibility stub
        pass


class ModelSerializer(Serializer):
    pass
