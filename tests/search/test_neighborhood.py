from collections.abc import Mapping
from dataclasses import dataclass

import pytest

from cvrp_tabu_search.routes import Coordinates, Route, Vehicle
from cvrp_tabu_search.search.moves import (
    Move,
    ReturnTabuKey,
    ReversalTabuKey,
    RouteUpdate,
    TabuKeyTuple,
)
from cvrp_tabu_search.search.neighborhood import find_best_neighbor
from cvrp_tabu_search.search.tabu import tabu_search


@dataclass(frozen=True)
class Problem:
    coordinates: Coordinates
    demands: list[int]
    fleet: list[Vehicle]
    current_cost: int


def _vehicle(capacity: int, route: Route, load: int) -> Vehicle:
    vehicle = Vehicle(capacity)
    vehicle.route = route
    vehicle.load = load
    return vehicle


@pytest.fixture
def relocation_problem() -> Problem:
    # Customer 3 is far from 2 and close to 4. A swap would overload vehicle 0.
    return Problem(
        coordinates=[(0, 0), (1, 0), (10, 0), (11, 0)],
        demands=[0, 3, 3, 4],
        fleet=[_vehicle(6, [2, 3], 6), _vehicle(7, [4], 4)],
        current_cost=42,
    )


@pytest.fixture
def swap_problem() -> Problem:
    # Neither route can accept a relocation. Swaps can uncross the routes.
    return Problem(
        coordinates=[(0, 0), (-3, 0), (0, 4), (0, 5), (-3, 1)],
        demands=[0, 2, 3, 3, 2],
        fleet=[_vehicle(6, [2, 3], 5), _vehicle(6, [4, 5], 5)],
        current_cost=25,
    )


def _select_move(
    problem: Problem,
    *,
    tabu_list: Mapping[TabuKeyTuple, int] | None = None,
    best_cost: int | None = None,
    intensify: bool = False,
    frequencies: Mapping[int, int] | None = None,
    diversify: bool = False,
) -> Move | None:
    return find_best_neighbor(
        problem.fleet,
        problem.current_cost,
        problem.coordinates,
        depot=1,
        demands=problem.demands,
        tabu_list=tabu_list or {},
        iteration=3,
        best_cost=problem.current_cost if best_cost is None else best_cost,
        frequencies=frequencies or {},
        intensify=intensify,
        diversify=diversify,
    )


def test_relocation_selects_the_best_feasible_insertion(
    relocation_problem: Problem,
) -> None:
    move = _select_move(relocation_problem)

    assert move == Move(
        route_updates=(RouteUpdate(0, [2], 3), RouteUpdate(1, [3, 4], 7)),
        cost=24,
        tabu_keys=(ReturnTabuKey("return", 3, 0),),
        customers=(3,),
    )
    assert [vehicle.route for vehicle in relocation_problem.fleet] == [[2, 3], [4]]
    assert [vehicle.load for vehicle in relocation_problem.fleet] == [6, 4]


def test_relocation_rejects_overloading_the_destination(
    relocation_problem: Problem,
) -> None:
    # The improvement found with capacity 7 is infeasible with capacity 6.
    relocation_problem.fleet[1].capacity = 6

    move = _select_move(relocation_problem)

    assert move is not None
    assert move.route_updates == ((0, [3, 2], 6),)
    assert move.cost == 42


def test_advanced_search_applies_relocation_and_updates_both_loads(
    relocation_problem: Problem,
) -> None:
    fleet = relocation_problem.fleet

    best_routes, best_cost, history = tabu_search(
        fleet,
        relocation_problem.coordinates,
        depot=1,
        tabu_tenure=(2, 2),
        max_iterations=1,
        stagnation_limit=5,
        start_time=0.0,
        demands=relocation_problem.demands,
    )

    assert best_routes == [[2], [3, 4]]
    assert best_cost == 24
    assert [vehicle.route for vehicle in fleet] == best_routes
    assert [vehicle.load for vehicle in fleet] == [3, 7]
    assert [(iteration, best, current) for iteration, best, _, current in history] == [
        (0, 42, 42),
        (1, 24, 24),
    ]


def test_swap_keeps_the_first_candidate_when_costs_tie(swap_problem: Problem) -> None:
    move = _select_move(swap_problem)

    assert move == Move(
        route_updates=(RouteUpdate(0, [4, 3], 6), RouteUpdate(1, [2, 5], 4)),
        cost=17,
        tabu_keys=(ReturnTabuKey("return", 2, 0), ReturnTabuKey("return", 4, 1)),
        customers=(2, 4),
    )


@pytest.mark.parametrize(
    "blocked_key",
    [("return", 2, 1), ("return", 4, 0)],
    ids=["first-customer", "second-customer"],
)
def test_either_tabu_key_blocks_a_swap_at_a_tied_best_cost(
    swap_problem: Problem, blocked_key: TabuKeyTuple
) -> None:
    move = _select_move(swap_problem, tabu_list={blocked_key: 3}, best_cost=17)

    assert move == Move(
        route_updates=(RouteUpdate(0, [2, 5], 4), RouteUpdate(1, [4, 3], 6)),
        cost=17,
        tabu_keys=(ReturnTabuKey("return", 3, 0), ReturnTabuKey("return", 5, 1)),
        customers=(3, 5),
    )


@pytest.mark.parametrize(
    ("first_demand", "second_demand"),
    [(1, 2), (2, 1)],
    ids=["first-route", "second-route"],
)
def test_swap_rejects_overloading_either_vehicle(
    first_demand: int, second_demand: int
) -> None:
    problem = Problem(
        coordinates=[(0, 0), (1, 0), (2, 0)],
        demands=[0, first_demand, second_demand],
        fleet=[
            _vehicle(first_demand, [2], first_demand),
            _vehicle(second_demand, [3], second_demand),
        ],
        current_cost=6,
    )

    assert _select_move(problem) is None


def test_relocation_cannot_remove_the_last_customer_from_a_route() -> None:
    problem = Problem(
        coordinates=[(0, 0), (1, 0), (2, 0)],
        demands=[0, 1, 1],
        fleet=[_vehicle(2, [2], 1), _vehicle(2, [3], 1)],
        current_cost=6,
    )

    move = _select_move(problem)

    # Combining the routes would cost 4. The best permitted move is the swap.
    assert move is not None
    assert move.cost == 6
    assert move.route_updates == ((0, [3], 1), (1, [2], 1))


def test_intensification_keeps_the_assignment_of_customers(
    relocation_problem: Problem,
) -> None:
    move = _select_move(relocation_problem, intensify=True)

    assert move == Move(
        route_updates=(RouteUpdate(0, [3, 2], 6),),
        cost=42,
        tabu_keys=(ReversalTabuKey("reverse", 2, 3),),
        customers=(),
    )


@pytest.mark.parametrize(
    ("use_phases", "expected_assignments", "expected_loads"),
    [
        (True, [[2], [3, 4]], [2, 4]),
        (False, [[4], [2, 3]], [3, 3]),
    ],
    ids=["restores-best-assignment", "continues-current-assignment"],
)
def test_intensification_restores_the_best_assignment_and_vehicle_loads(
    use_phases: bool, expected_assignments: list[Route], expected_loads: list[int]
) -> None:
    # Equal distances allow the current assignment to change without improving the best cost.
    fleet = [_vehicle(8, [2], 2), _vehicle(8, [3, 4], 4)]
    coordinates = [(0, 0)] * 4
    demands = [0, 2, 1, 3]

    best_routes, best_cost, history = tabu_search(
        fleet,
        coordinates,
        depot=1,
        tabu_tenure=(2, 2),
        max_iterations=11,
        stagnation_limit=30,
        start_time=0.0,
        demands=demands,
        use_phases=use_phases,
    )

    assert best_routes == [[2], [3, 4]]
    assert best_cost == 0
    assert history[-1][0] == 11
    assert [sorted(vehicle.route) for vehicle in fleet] == expected_assignments
    assert [vehicle.load for vehicle in fleet] == expected_loads


def test_diversification_prefers_the_less_frequently_moved_customer(
    relocation_problem: Problem,
) -> None:
    # Moving customer 2 costs 42, while moving the more frequently selected 3 costs 24.
    move = _select_move(relocation_problem, diversify=True, frequencies={2: 1, 3: 5})

    assert move == Move(
        route_updates=(RouteUpdate(0, [3], 3), RouteUpdate(1, [2, 4], 7)),
        cost=42,
        tabu_keys=(ReturnTabuKey("return", 2, 0),),
        customers=(2,),
    )
