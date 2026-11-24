from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..solution import Solution
from .move import Move
from .tabu_keys import InversionTabuKey, MoveTabuKeys


@validated_dataclass(frozen=True)
class InversionMove(Move):
    """Reverse the visits between two inclusive indices on one route."""

    route_index: NonNegativeInt
    start_index: NonNegativeInt
    end_index: NonNegativeInt

    def tabu_keys(self, solution: Solution) -> MoveTabuKeys:
        route = solution.vehicle_at(self.route_index).route
        start_client = route.client_at(self.start_index)
        end_client = route.client_at(self.end_index)
        lower_client_id, upper_client_id = sorted((start_client.id, end_client.id))
        keys = (InversionTabuKey(lower_client_id, upper_client_id),)
        return MoveTabuKeys(to_check=keys, to_register=keys)

    def apply(self, solution: Solution) -> None:
        route = solution.vehicle_at(self.route_index).route
        route.reverse_segment(self.start_index, self.end_index)
