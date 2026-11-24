from abc import ABC, abstractmethod

from ..solution import Solution


class Move(ABC):
    @abstractmethod
    def apply(self, solution: Solution) -> None:
        """Apply the move to the solution in place."""


def _check_distinct_route_indices(first: int, second: int) -> None:
    if first == second:
        raise ValueError("The move requires two distinct routes.")
