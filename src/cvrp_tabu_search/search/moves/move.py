from abc import ABC, abstractmethod

from ..solution import Solution
from .tabu_keys import MoveTabuKeys


class Move(ABC):
    @abstractmethod
    def tabu_keys(self, solution: Solution) -> MoveTabuKeys:
        """Get the keys to check and register using the solution before the move."""

    @abstractmethod
    def apply(self, solution: Solution) -> None:
        """Apply the move to the solution in place."""


def _check_distinct_route_indices(first: int, second: int) -> None:
    if first == second:
        raise ValueError("The move requires two distinct routes.")
