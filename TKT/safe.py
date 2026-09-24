"""Safe function execution.

This module defines utilities for handling errors in a functional style.
Decorated functions return a `Result` object instead of raising
exceptions.  The `Result` explicitly represents either success or
failure.

Usage:
    The main entry point is the `safe` function, which is meant to be
    used as a decorator. When used as such, the decorated function
    returns a `Result` object instead of its usual return type. This
    object wraps either the return value if no error occurs, or an error
    object.

Design:
    - The `SafeFunction` class creates a wrapper that executes the
      stored function and returns a `Result` instead of its usual
      return value or raising an error.
    - The `Result` class is a wrapper around the return value. Its
      variants indicate whether the called function was successful or
      raised an error.
    - `Result` objects can provide the inner value with `unwrap`, or
      supply a default value using `unwrap_or`.
    - This pattern was inspired by a language named after a fungus that
      affects plants.
"""

import json
import os
import sys
from abc import ABC, abstractmethod

# Backwards-compatible typing imports
try:
    from typing import Any, Callable, Generic, Never, ParamSpec, TypeAlias, TypeVar
except ImportError:
    from typing import Any, Generic, TypeVar
    from collections.abc import Callable
    from typing_extensions import NoReturn, ParamSpec, TypeAlias

    Never = NoReturn  # type: ignore[assignment,misc]

T = TypeVar("T", covariant=True)
U = TypeVar("U")
E = TypeVar("E", bound=Exception)
F = TypeVar("F", bound=Exception)
P = ParamSpec("P")


class BaseResult(ABC, Generic[T, E]):
    """Base interface for Result types."""

    @abstractmethod
    def __bool__(self) -> bool:
        """Return True if the result is Ok, False if Err."""

    @abstractmethod
    def __and__(self, other: Any, /) -> Any:
        """Short-circuit logical AND with another Result."""

    @abstractmethod
    def __or__(self, other: Any, /) -> Any:
        """Short-circuit logical OR with another Result."""

    @abstractmethod
    def __eq__(self, other: Any, /) -> bool:
        """Compare this result with another value."""

    @abstractmethod
    def unwrap(self) -> T:
        """Return the contained value or raise the contained error."""

    @abstractmethod
    def unwrap_or(self, default: U, /) -> "T | U":
        """Return the contained value or the default."""

    @abstractmethod
    def map(self, op: Callable[[T], U], /) -> "BaseResult[U, E]":
        """Apply an operation to an Ok value."""

    @abstractmethod
    def map_or(self, default: U, op: Callable[[T], U], /) -> U:
        """Apply an operation to an Ok value or return the default."""

    @abstractmethod
    def map_err(self, op: Callable[[E], F], /) -> "BaseResult[T, F]":
        """Apply an operation to an Err value."""

    @property
    @abstractmethod
    def is_ok(self) -> bool:
        """Return True if the result is Ok."""

    @property
    @abstractmethod
    def is_err(self) -> bool:
        """Return True if the result is Err."""

    @property
    @abstractmethod
    def ok(self) -> "T | None":
        """Return the contained value if Ok."""

    @property
    @abstractmethod
    def err(self) -> "E | None":
        """Return the contained error if Err."""


class Ok(BaseResult[T, Any]):
    """Successful Result variant."""

    __slots__ = ("_value",)
    __match_args__ = ("_value",)

    def __init__(self, value: T, /):
        self._value = value

    def __bool__(self) -> bool:
        return True

    def __and__(self, other: Any, /) -> Any:
        return other

    def __or__(self, other: Any, /) -> Any:
        return self

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, Ok):
            return self.ok == other.ok
        return False

    def __repr__(self) -> str:
        return f"Ok({self._value!r})"

    def unwrap(self) -> T:
        return self._value

    def unwrap_or(self, default: Any, /) -> T:
        return self._value

    def map(self, op: Callable[[T], U], /) -> "Ok[U]":
        return Ok(op(self._value))

    def map_or(self, default: U, op: Callable[[T], U], /) -> U:
        return op(self._value)

    def map_err(self, op: Callable[[E], F], /) -> "Ok[T]":
        return self

    @property
    def is_ok(self) -> bool:
        return True

    @property
    def is_err(self) -> bool:
        return False

    @property
    def ok(self) -> T:
        return self._value

    @property
    def err(self) -> None:
        return None


class Err(BaseResult[Never, E]):
    """Failed Result variant."""

    __slots__ = ("_error",)
    __match_args__ = ("_error",)

    def __init__(self, error: E, /):
        self._error = error

    def __bool__(self) -> bool:
        return False

    def __and__(self, other: Any, /) -> Any:
        return self

    def __or__(self, other: Any, /) -> Any:
        return other

    def __eq__(self, other: Any, /) -> bool:
        if isinstance(other, Err):
            return self._error == other._error
        return False

    def __repr__(self) -> str:
        return f"Err({self._error!r})"

    def unwrap(self) -> Never:
        raise self._error

    def unwrap_or(self, default: U, /) -> U:
        return default

    def map(self, op: Callable[[T], U], /) -> "Err[E]":
        return self

    def map_or(self, default: U, op: Callable[[T], U], /) -> U:
        return default

    def map_err(self, op: Callable[[E], F], /) -> "Err[F]":
        return Err(op(self._error))

    @property
    def is_ok(self) -> bool:
        return False

    @property
    def is_err(self) -> bool:
        return True

    @property
    def ok(self) -> None:
        return None

    @property
    def err(self) -> E:
        return self._error


Result: TypeAlias = "Ok[Any] | Err[Any]"


class SafeFunction(Generic[P, T]):
    """Wraps a function to return a Result instead of raising exceptions."""

    def __init__(self, func: Callable[P, T]):
        self._func = func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> Result:
        try:
            return Ok(self._func(*args, **kwargs))
        except Exception as err:
            return Err(err)


def safe(func: Callable[P, T]) -> SafeFunction[P, T]:
    """Decorate a function to return a Result instead of raising exceptions."""
    if json.loads(os.environ.get("TKT_DEBUG", "false")):
        return func  # type: ignore[return-value]
    return SafeFunction(func)
