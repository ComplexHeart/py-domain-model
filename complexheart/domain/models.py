import inspect
from dataclasses import is_dataclass
from typing import List, Callable, Generator, Any, Union, Dict, Optional, Type

from complexheart.domain.event import DomainEvent

INVARIANT_NAME = 0
INVARIANT_METHOD = 1
INVARIANT_FN_WRAPPER = 'wrapper_fn_invariant'
INVARIANT_INVALID_RETURN_TYPE_MESSAGE = 'Invariant return value must be boolean.'
INVARIANT_VIOLATION_MESSAGE = 'Unable create {object_name} due to {error}'
METHOD__INIT = '__init__'
METHOD__POST_INIT = '__post_init__'


class InvariantViolation(ValueError):
    pass


def _is_init(method: str) -> bool:
    return METHOD__INIT in str(method)


def _is_post_init(method: str) -> bool:
    return METHOD__POST_INIT in str(method) and not _is_init(method)


def _has__init__(cls: object) -> bool:
    return len(inspect.getmembers(cls, _is_init)) > 0


def _has__post_init__(cls: object) -> bool:
    return len(inspect.getmembers(cls, _is_post_init)) > 0


def invariant(fn: Callable) -> Callable:
    def _wrapper_fn_invariant(self, *args, **kwargs):
        return fn(self, *args, **kwargs)

    return _wrapper_fn_invariant


def has_invariants(cls) -> Type:
    # Depends on the dataclass package to initialize the class.
    # and register a post init function to execute the invariants.
    # https://docs.python.org/3/library/dataclasses.html#post-init-processing
    if _has__post_init__(cls):
        _original = cls.__post_init__

        def __invariant_post_init__(self, *args, **kwargs):
            _check_invariants(self)
            _original(self, *args, **kwargs)

        # override the original __post_init__ method.
        cls.__post_init__ = __invariant_post_init__
    else:
        cls.__post_init__ = _check_invariants

    return cls


def _check_invariants(self: object) -> None:
    def _make_exception(object_name: str, error: str) -> InvariantViolation:
        return InvariantViolation(INVARIANT_VIOLATION_MESSAGE.format(
            object_name=object_name,
            error=error,
        ))

    for invariant_fn in _get_invariants(self.__class__):
        try:
            invariant_fn[INVARIANT_METHOD](self)
        except Exception as e:
            raise _make_exception(
                object_name=self.__class__.__name__,
                error=str(e),
            )


def _get_invariants(cls: object) -> Generator:
    def _is_invariant(method: str) -> bool:
        return INVARIANT_FN_WRAPPER in str(method) and METHOD__INIT not in str(method)

    for member in inspect.getmembers(cls, _is_invariant):
        yield member[INVARIANT_NAME], member[INVARIANT_METHOD]


class Model:
    def __init__(self, *args, **kwargs):
        cls = self.__class__.__mro__[0]
        cls_annotations = cls.__dict__.get('__annotations__', {})

        defaults = {name: getattr(cls, name, None)
                    for name, type in cls_annotations.items()}

        allowed_attributes = list(defaults.keys())
        for i_arg, value in enumerate(args):
            setattr(self, allowed_attributes[i_arg], value)

    def hydrate(self, attributes: Dict[str, Any]) -> None:
        for key, value in attributes.items():
            setattr(self, key, value)


class HasIdentity:
    pass


class HasEquality:
    pass


class ImmutableException(Exception):
    pass


class HasImmutability:
    def __setitem__(self, key: str, value: Any) -> None:
        raise ImmutableException("Modification of an immutable value object not allowed")


@has_invariants
class HasInvariants:
    pass


class HasDomainEvents:
    __domain_events: List[DomainEvent] = []

    def domain_events(self) -> List[DomainEvent]:
        return self.__domain_events
