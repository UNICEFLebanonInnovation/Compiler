"""Small compatibility layer for :mod:`model_utils`."""

from typing import Iterable, Tuple


class _Choices(tuple):
    def __new__(cls, items: Iterable[Tuple[str, str]]):
        obj = super().__new__(cls, items)
        for value, _label in items:
            setattr(obj, str(value), value)
        return obj


def Choices(*choices):
    """Return an iterable behaving similarly to ``model_utils.Choices``."""

    flat = []
    for choice in choices:
        if isinstance(choice, (list, tuple)):
            if len(choice) == 2 and not isinstance(choice[1], (list, tuple)):
                flat.append((choice[0], choice[1]))
            else:  # pragma: no cover - nested/grouped choices are collapsed
                key = choice[0]
                label = choice[1] if len(choice) > 1 else key
                flat.append((key, label))
        else:
            flat.append((choice, str(choice)))

    return _Choices(tuple(flat))
