from collections.abc import Iterator, Sequence
from dataclasses import dataclass
from itertools import combinations, permutations

from ...domain import Route
from ..solution import Solution
from .exchange_move import ExchangeMove
from .inversion_move import InversionMove
from .move import Move
from .reallocation_move import ReallocationMove


@dataclass(frozen=True)
class _RouteState:
    index: int
    route: Route
    load: int
    capacity: int


class Neighbourhood:
    @staticmethod
    def generate_moves(solution: Solution) -> Iterator[Move]:
        """Generate moves for a feasible solution.

        Consume the iterator before applying any move to the solution.
        """
        routes = tuple(
            _RouteState(
                index=index,
                route=vehicle.route,
                load=vehicle.route.total_demand,
                capacity=vehicle.capacity,
            )
            for index, vehicle in enumerate(solution.vehicles)
        )
        yield from Neighbourhood._generate_inversions(routes)
        yield from Neighbourhood._generate_reallocations(routes)
        yield from Neighbourhood._generate_exchanges(routes)

    @staticmethod
    def _generate_inversions(routes: Sequence[_RouteState]) -> Iterator[InversionMove]:
        for state in routes:
            client_indices = range(len(state.route))
            for start_index, end_index in combinations(client_indices, 2):
                yield InversionMove(
                    route_index=state.index,
                    start_index=start_index,
                    end_index=end_index,
                )

    @staticmethod
    def _generate_reallocations(
        routes: Sequence[_RouteState],
    ) -> Iterator[ReallocationMove]:
        for source, target in permutations(routes, 2):
            if len(source.route) < 2:
                # A relocation must leave at least one client in the source route.
                continue
            yield from Neighbourhood._generate_reallocations_between(source, target)

    @staticmethod
    def _generate_reallocations_between(
        source: _RouteState, target: _RouteState
    ) -> Iterator[ReallocationMove]:
        available_capacity = target.capacity - target.load
        insertion_indices = range(len(target.route) + 1)
        for source_client_index, client in enumerate(source.route):
            if client.demand > available_capacity:
                continue
            for target_client_index in insertion_indices:
                yield ReallocationMove(
                    source_route_index=source.index,
                    source_client_index=source_client_index,
                    target_route_index=target.index,
                    target_client_index=target_client_index,
                )

    @staticmethod
    def _generate_exchanges(routes: Sequence[_RouteState]) -> Iterator[ExchangeMove]:
        for first, second in combinations(routes, 2):
            yield from Neighbourhood._generate_exchanges_between(first, second)

    @staticmethod
    def _generate_exchanges_between(
        first: _RouteState, second: _RouteState
    ) -> Iterator[ExchangeMove]:
        for first_client_index, first_client in enumerate(first.route):
            for second_client_index, second_client in enumerate(second.route):
                demand_delta = second_client.demand - first_client.demand
                first_load = first.load + demand_delta
                second_load = second.load - demand_delta
                if first_load > first.capacity or second_load > second.capacity:
                    continue

                yield ExchangeMove(
                    first_route_index=first.index,
                    first_client_index=first_client_index,
                    second_route_index=second.index,
                    second_client_index=second_client_index,
                )
