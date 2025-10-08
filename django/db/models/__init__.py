"""In-memory ORM primitives to support the unit tests without Django."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, List, Optional


class Field:
    def __init__(self, *args: Any, **kwargs: Any):  # noqa: D401 - mirror Django signature
        self.args = args
        self.kwargs = kwargs


class CharField(Field):
    pass


class URLField(Field):
    pass


class TextField(Field):
    pass


class IntegerField(Field):
    pass


class PositiveSmallIntegerField(Field):
    pass


class BooleanField(Field):
    pass


class DateField(Field):
    pass


class DateTimeField(Field):
    pass


class JSONField(Field):
    def __init__(self, *args: Any, default=None, **kwargs: Any):
        super().__init__(*args, **kwargs)
        self.default = default


class ForeignKey(Field):
    def __init__(self, to, *args: Any, **kwargs: Any):
        super().__init__(to, *args, **kwargs)
        self.related_model = to


class ManyToManyField(Field):
    pass


class ImageField(Field):
    pass


class FileField(Field):
    pass


class FloatField(Field):
    pass


class DecimalField(Field):
    pass


class EmailField(Field):
    pass


class SlugField(Field):
    pass


CASCADE = 'CASCADE'
SET_NULL = 'SET_NULL'


class Q(dict):
    pass


class Count:
    def __init__(self, field: str, **kwargs: Any):  # noqa: D401 - mimic Django signature
        self.field = field
        self.kwargs = kwargs


class Exists:
    def __init__(self, queryset=None):
        self.queryset = queryset


class OuterRef:
    def __init__(self, field):
        self.field = field


class Subquery:
    def __init__(self, queryset):
        self.queryset = queryset


class InMemoryManager:
    def __init__(self, model=None):
        self.model = model
        self._items: List[Any] = []

    def add(self, instance):
        if instance not in self._items:
            self._items.append(instance)

    def create(self, **kwargs):
        if self.model is None:
            raise LookupError('Manager is not bound to a model')
        instance = self.model(**kwargs)
        instance.save()
        return instance

    def all(self):
        return list(self._items)

    def filter(self, **kwargs):
        return [item for item in self._items if _matches(item, kwargs)]

    def get(self, **kwargs):
        matches = self.filter(**kwargs)
        if not matches:
            raise LookupError('Object does not exist')
        if len(matches) > 1:
            raise LookupError('Multiple objects returned')
        return matches[0]

    def dates(self, field: str, kind: str):  # noqa: D401 - compatibility stub
        return []


def _matches(instance: Any, kwargs: dict) -> bool:
    for key, value in kwargs.items():
        if getattr(instance, key, None) != value:
            return False
    return True


class ModelMeta(type):
    def __new__(mcls, name, bases, attrs):
        cls = super().__new__(mcls, name, bases, attrs)
        if name != 'Model':
            manager = attrs.get('objects')
            if isinstance(manager, InMemoryManager):
                manager.model = cls
                cls.objects = manager
            else:
                cls.objects = InMemoryManager(cls)
        return cls


class Model(metaclass=ModelMeta):
    def __init__(self, **kwargs: Any):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def save(self):
        self.__class__.objects.add(self)


class Manager(InMemoryManager):
    pass


