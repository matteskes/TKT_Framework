"""
Safe function execution.

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

from typing import Callable, Generic, TypeVar

T = TypeVar("T")
E = TypeVar("E", bound=Exception)


class Result(Generic[T, E]):
    """
    A generic container holding either a return value (`ok`) or an
    exception (`err`). Provides convenience methods like `unwrap` and
    `unwrap_or`.
    """

    def __init__(self, *, ok: T | None = None, err: E | None = None):
        if not ((ok is None) ^ (err is None)):
            raise ValueError("Result must have exactly one of ok or err")
        self.ok = ok
        self.err = err

    def __repr__(self):
        if self.is_ok:
            return f"Result(ok={self.ok!r})"
        else:
            return f"Result(err={self.err!r})"

    @property
    def is_ok(self):
        return self.err is None

    @property
    def is_err(self):
        return self.err is not None

    def unwrap(self):
        if self.is_ok:
            return self.ok
        raise self.err

    def unwrap_or(self, default, /):
        return self.ok if self.is_ok else default


class SafeFunction:
    """
    Callable wrapper that executes a function and captures raised
    exceptions as `Result` objects.
    """

    def __init__(self, func: Callable, /):
        self._func = func

    def __call__(self, *args, **kwargs) -> Result:
        try:
            return Result(ok=self._func(*args, **kwargs))
        except Exception as err:
            return Result(err=err)


def safe(func: Callable):
    """A decorator for functions that can raise errors."""
    return SafeFunction(func)
