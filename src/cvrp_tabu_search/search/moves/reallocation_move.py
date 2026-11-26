from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..solution import Solution
from .move import Move, _check_distinct_route_indices
from .tabu_keys import MoveTabuKeys, ReturnTabuKey


@validated_dataclass(frozen=True)
class ReallocationMove(Move):
    """Move a client to an insertion index on a different route."""

    source_route_index: NonNegativeInt
    source_client_index: NonNegativeInt
    target_route_index: NonNegativeInt
    target_client_index: NonNegativeInt

    def __post_init__(self) -> None:
        _check_distinct_route_indices(self.source_route_index, self.target_route_index)

    def tabu_keys(self, solution: Solution) -> MoveTabuKeys:
        source = solution.vehicle_at(self.source_route_index)
        client = source.route.client_at(self.source_client_index)
        return MoveTabuKeys(
            to_check=(ReturnTabuKey(client.id, self.target_route_index),),
            to_register=(ReturnTabuKey(client.id, self.source_route_index),),
        )

    def apply(self, solution: Solution) -> None:
        source, target = solution.vehicles_with_distinct_routes(
            self.source_route_index, self.target_route_index
        )
        client = source.route.client_at(self.source_client_index)
        remaining_demand = source.route.total_demand - client.demand
        source.check_capacity(remaining_demand)

        target.insert_client(self.target_client_index, client)
        source.remove_client(self.source_client_index)
