import inspect
from typing import Callable, Generator, Type

INVARIANT_NAME = 0
INVARIANT_METHOD = 1
INVARIANT_FN_WRAPPER = 'wrapper_fn_invariant'
INVARIANT_INVALID_RETURN_TYPE_MESSAGE = 'Invariant return value must be boolean.'
INVARIANT_VIOLATION_MESSAGE = 'Unable create {object_name} due to {error}'
METHOD__INIT = '__init__'
METHOD__POST_INIT = '__post_init__'


class InvariantViolation(Exception):
    pass


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
        setattr(cls, METHOD__POST_INIT, _check_invariants)

    return cls


def invariant(fn: Callable) -> Callable:
    def _wrapper_fn_invariant(self, *args, **kwargs):
        return fn(self, *args, **kwargs)

    return _wrapper_fn_invariant


def _has__post_init__(cls: object) -> bool:
    def _is_post_init(method: str) -> bool:
        return METHOD__POST_INIT in str(method) and METHOD__INIT not in str(method)

    return len(inspect.getmembers(cls, _is_post_init)) > 0


def _check_invariants(self: object) -> None:
    def _make_exception(object_name: str, error: str) -> InvariantViolation:
        return InvariantViolation(INVARIANT_VIOLATION_MESSAGE.format(
            object_name=object_name,
            error=error,
        ))

    for invariant_fn in _get_invariants(self.__class__):
        try:
            if not invariant_fn[INVARIANT_METHOD](self):
                raise _make_exception(
                    object_name=self.__class__.__name__,
                    error=invariant_fn[INVARIANT_NAME].replace("_", " "),
                )

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
