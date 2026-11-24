from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..solution import Solution
from .move import Move, _check_distinct_route_indices


@validated_dataclass(frozen=True)
class ExchangeMove(Move):
    """Trade the clients at two visit indices on different routes."""

    first_route_index: NonNegativeInt
    first_client_index: NonNegativeInt
    second_route_index: NonNegativeInt
    second_client_index: NonNegativeInt

    def __post_init__(self) -> None:
        _check_distinct_route_indices(self.first_route_index, self.second_route_index)

    def apply(self, solution: Solution) -> None:
        first = solution.vehicle_at(self.first_route_index)
        second = solution.vehicle_at(self.second_route_index)
        first.exchange_clients(
            self.first_client_index, second, self.second_client_index
        )
