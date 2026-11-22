from collections.abc import Mapping, Sequence
from typing import Literal, NamedTuple

from .routes import Coordinates, Route, Vehicle, route_cost
from .search import evaluate_reversals, is_tabu

type TabuKeyTuple = tuple[Literal["reverse", "return"], int, int]


class ReversalTabuKey(NamedTuple):
    kind: Literal["reverse"]
    lower_customer: int
    upper_customer: int


class ReturnTabuKey(NamedTuple):
    kind: Literal["return"]
    customer: int
    vehicle_index: int


type TabuKey = ReversalTabuKey | ReturnTabuKey


class RouteUpdate(NamedTuple):
    vehicle_index: int
    route: Route
    load: int


class Move(NamedTuple):
    route_updates: tuple[RouteUpdate, ...]
    cost: int
    tabu_keys: tuple[TabuKey, ...]
    customers: tuple[int, ...]


class _RoutePair(NamedTuple):
    source_index: int
    target_index: int
    source: Vehicle
    target: Vehicle
    cost_without_routes: int


def find_best_neighbor(
    fleet: Sequence[Vehicle],
    current_cost: int,
    coordinates: Coordinates,
    depot: int,
    demands: Sequence[int],
    tabu_list: Mapping[TabuKeyTuple, int],
    iteration: int,
    best_cost: int,
    frequencies: Mapping[int, int],
    *,
    intensify: bool = False,
    diversify: bool = False,
) -> Move | None:
    neighborhood = _Neighborhood(fleet, current_cost, coordinates, depot, demands)
    selector = _MoveSelector(
        tabu_list, iteration, best_cost, frequencies, diversify=diversify
    )
    neighborhood.evaluate(selector, intensify=intensify, diversify=diversify)
    return selector.best_move


def _named_tabu_key(key: TabuKeyTuple) -> TabuKey:
    kind, first, second = key
    if kind == "reverse":
        return ReversalTabuKey(kind, first, second)

    return ReturnTabuKey(kind, first, second)


class _MoveSelector:
    def __init__(
        self,
        tabu_list: Mapping[TabuKeyTuple, int],
        iteration: int,
        best_cost: int,
        frequencies: Mapping[int, int],
        *,
        diversify: bool,
    ) -> None:
        self._tabu_list = tabu_list
        self._iteration = iteration
        self._best_cost = best_cost
        self._frequencies = frequencies
        self._diversify = diversify
        self._best_priority: tuple[int, ...] | None = None
        self.best_move: Move | None = None

    def consider(
        self,
        route_updates: tuple[tuple[int, Route, int], ...],
        cost: int,
        test_keys: tuple[TabuKeyTuple, ...],
        tabu_keys: tuple[TabuKeyTuple, ...],
        customers: tuple[int, ...],
    ) -> None:
        for key in test_keys:
            if is_tabu(self._tabu_list, key, self._iteration, cost, self._best_cost):
                return

        priority: tuple[int, ...] = (cost,)
        if self._diversify:
            move_frequency = sum(
                self._frequencies.get(customer, 0) for customer in customers
            )
            priority = (move_frequency, cost)

        if self._best_priority is None or priority < self._best_priority:
            self._best_priority = priority
            # Build named records only when a candidate becomes the best move.
            self.best_move = Move(
                route_updates=tuple(RouteUpdate(*update) for update in route_updates),
                cost=cost,
                tabu_keys=tuple(_named_tabu_key(key) for key in tabu_keys),
                customers=customers,
            )


class _Neighborhood:
    def __init__(
        self,
        fleet: Sequence[Vehicle],
        current_cost: int,
        coordinates: Coordinates,
        depot: int,
        demands: Sequence[int],
    ) -> None:
        self._fleet = fleet
        self._current_cost = current_cost
        self._coordinates = coordinates
        self._depot = depot
        self._demands = demands
        self._route_costs = [
            route_cost(vehicle.route, coordinates, depot) for vehicle in fleet
        ]

    def evaluate(
        self, selector: _MoveSelector, *, intensify: bool, diversify: bool
    ) -> None:
        for index, vehicle in enumerate(self._fleet):
            if not diversify:
                self._evaluate_reversals(index, vehicle, selector)

            # Intensification keeps the customer assignment of the best solution.
            if not intensify:
                self._evaluate_inter_route_moves(index, vehicle, selector)

    def _evaluate_reversals(
        self, index: int, vehicle: Vehicle, selector: _MoveSelector
    ) -> None:
        cost_without_route = self._current_cost - self._route_costs[index]
        reversals = evaluate_reversals(
            vehicle.route, self._coordinates, self._depot, cost_without_route
        )

        for reversal in reversals:
            key: TabuKeyTuple = ("reverse", *reversal.key)
            updates = ((index, reversal.route, vehicle.load),)
            selector.consider(updates, reversal.cost, (key,), (key,), ())

    def _evaluate_inter_route_moves(
        self, source_index: int, source: Vehicle, selector: _MoveSelector
    ) -> None:
        cost_without_source = self._current_cost - self._route_costs[source_index]
        for target_index, target in enumerate(self._fleet):
            if source_index == target_index:
                continue

            cost_without_routes = cost_without_source - self._route_costs[target_index]
            pair = _RoutePair(
                source_index, target_index, source, target, cost_without_routes
            )
            for position, customer in enumerate(source.route):
                demand = self._demands[customer - 1]
                self._evaluate_relocations(pair, position, customer, demand, selector)

                # Each pair of vehicles only needs to be considered once for swaps.
                if target_index > source_index:
                    self._evaluate_swaps(pair, position, customer, demand, selector)

    def _evaluate_relocations(
        self,
        pair: _RoutePair,
        position: int,
        customer: int,
        demand: int,
        selector: _MoveSelector,
    ) -> None:
        target_load = pair.target.load + demand
        # Removing the last customer would leave the source route unused.
        if len(pair.source.route) <= 1 or target_load > pair.target.capacity:
            return

        source_route = pair.source.route.copy()
        source_route.pop(position)
        coordinates, depot = self._coordinates, self._depot
        cost_without_customer = pair.cost_without_routes + route_cost(
            source_route, coordinates, depot
        )
        source_load = pair.source.load - demand
        source_update = (pair.source_index, source_route, source_load)
        test_keys: tuple[TabuKeyTuple, ...] = (("return", customer, pair.target_index),)
        tabu_keys: tuple[TabuKeyTuple, ...] = (("return", customer, pair.source_index),)
        customers = (customer,)

        for target_position in range(len(pair.target.route) + 1):
            target_route = pair.target.route.copy()
            target_route.insert(target_position, customer)
            cost = cost_without_customer + route_cost(target_route, coordinates, depot)
            updates = (source_update, (pair.target_index, target_route, target_load))
            selector.consider(updates, cost, test_keys, tabu_keys, customers)

    def _evaluate_swaps(
        self,
        pair: _RoutePair,
        position: int,
        customer: int,
        demand: int,
        selector: _MoveSelector,
    ) -> None:
        coordinates, depot = self._coordinates, self._depot
        for target_position, target_customer in enumerate(pair.target.route):
            target_demand = self._demands[target_customer - 1]
            source_load = pair.source.load - demand + target_demand
            target_load = pair.target.load - target_demand + demand
            if source_load > pair.source.capacity or target_load > pair.target.capacity:
                continue

            source_route = pair.source.route.copy()
            target_route = pair.target.route.copy()
            source_route[position] = target_customer
            target_route[target_position] = customer
            cost = (
                pair.cost_without_routes
                + route_cost(source_route, coordinates, depot)
                + route_cost(target_route, coordinates, depot)
            )
            updates = (
                (pair.source_index, source_route, source_load),
                (pair.target_index, target_route, target_load),
            )
            test_keys: tuple[TabuKeyTuple, ...] = (
                ("return", customer, pair.target_index),
                ("return", target_customer, pair.source_index),
            )
            tabu_keys: tuple[TabuKeyTuple, ...] = (
                ("return", customer, pair.source_index),
                ("return", target_customer, pair.target_index),
            )
            selector.consider(
                updates, cost, test_keys, tabu_keys, (customer, target_customer)
            )
