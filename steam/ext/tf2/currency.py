"""A nice way to work with TF2's currencies."""

from __future__ import annotations

from abc import ABCMeta
from fractions import Fraction
from types import FunctionType
from typing import Any, overload

from typing_extensions import Literal

from ... import utils

__all__ = ("Metal",)


class MetalMeta(ABCMeta):
    """Necessitated by Fraction dunders not using self.__class__ for returns. You can ignore this class."""

    def __new__(mcs, name: str, bases: tuple[type, ...], namespace: dict[str, Any]) -> type[Metal]:
        for name_, function in Fraction.__dict__.items():
            if (
                isinstance(function, FunctionType)
                and name_.startswith("__")
                and name_.endswith("__")
                and function.__qualname__ not in (name_, f"Fraction.{name_}")
            ):
                exec(
                    f"def {name_}(self, other):\n"
                    f"    return self.__class__(Fraction.{name_}(self, other) * 9)\n"
                    f"namespace[{name_!r}] = {name_}\n"
                )
        return super().__new__(mcs, name, bases, namespace)


class Metal(Fraction, metaclass=MetalMeta):
    """A class to represent some metal in TF2.

    The value used as the denominator corresponds to one scrap metal.
    """

    __slots__ = ()

    @overload
    def __new__(cls, value: utils.Intable, /) -> Metal:
        ...

    def __new__(cls, value, /, *, _normalize: bool = ...) -> Metal:
        if isinstance(value, float):  # 1.222222222222223
            units, _, decimals = str(value).partition(".")
            if len(decimals) < 2 or decimals[0] != decimals[1]:
                raise ValueError("metal value is invalid")
            value = int(units) * 9 + int(decimals[0])
        elif isinstance(value, str):  # '1.22'
            units, _, decimals = value.partition(".")
            if len(decimals) != 2 or decimals[0] != decimals[1]:
                raise ValueError("metal value is invalid")
            value = int(units) * 9 + int(decimals[0])

        self = object.__new__(cls)
        try:
            self._numerator = int(value)
        except (ValueError, TypeError):
            raise TypeError("non-int passed to Metal.__new__, that could not be cast")

        return self

    @property
    def denominator(self) -> Literal[9]:
        return 9

    def __str__(self) -> str:
        units, _, decimals = f"{self._numerator / 9}".partition(".")
        return f"{units}.{decimals[:2]}"

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._numerator})"
