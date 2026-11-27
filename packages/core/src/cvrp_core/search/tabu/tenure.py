from random import Random

from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass


@validated_dataclass(frozen=True)
class TabuTenure:
    """Configure an inclusive range of tabu durations in iterations."""

    minimum: NonNegativeInt
    maximum: NonNegativeInt

    def __post_init__(self) -> None:
        if self.minimum > self.maximum:
            raise ValueError("Minimum tabu tenure must not exceed the maximum.")

    def draw(self, generator: Random) -> int:
        """Return the fixed duration or draw from the inclusive range."""
        if self.minimum == self.maximum:
            return self.minimum

        return generator.randint(self.minimum, self.maximum)


DEFAULT_TABU_TENURE = TabuTenure(minimum=1, maximum=15)
