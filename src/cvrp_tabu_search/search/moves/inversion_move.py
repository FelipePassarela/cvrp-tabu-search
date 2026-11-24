from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..solution import Solution
from .move import Move


@validated_dataclass(frozen=True)
class InversionMove(Move):
    """Reverse the visits between two inclusive indices on one route."""

    route_index: NonNegativeInt
    start_index: NonNegativeInt
    end_index: NonNegativeInt

    def apply(self, solution: Solution) -> None:
        route = solution.vehicle_at(self.route_index).route
        route.reverse_segment(self.start_index, self.end_index)
