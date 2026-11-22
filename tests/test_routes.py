import pytest

from cvrp_tabu_search.routes import (
    Route,
    Vehicle,
    build_initial_solution,
    distance,
    reverse_segment,
    route_cost,
)


def test_vehicle_accepts_a_customer_that_fills_its_capacity() -> None:
    vehicle = Vehicle(capacity=5)
    assert vehicle.add_customer(customer=2, demand=2)

    accepted = vehicle.add_customer(customer=3, demand=3)

    assert accepted
    assert vehicle.load == 5
    assert vehicle.route == [2, 3]


def test_vehicle_rejects_overload_without_changing_its_route() -> None:
    vehicle = Vehicle(capacity=5)
    assert vehicle.add_customer(customer=2, demand=4)

    accepted = vehicle.add_customer(customer=3, demand=2)

    assert not accepted
    assert vehicle.load == 4
    assert vehicle.route == [2]


@pytest.mark.parametrize(
    ("separation", "expected"),
    [(1.49, 1), (1.5, 2), (2.5, 3)],
    ids=["below-half", "round-up", "round-up-from-even"],
)
def test_distance_uses_tsplib_rounding(separation: float, expected: int) -> None:
    coordinates = [(0.0, 0.0), (separation, 0.0), (20.0, 20.0)]

    assert distance(1, 2, coordinates) == expected
    assert distance(2, 1, coordinates) == expected


@pytest.mark.parametrize(
    ("route", "expected_cost"),
    [([1, 3], 12), ([1], 6), ([], 0)],
    ids=["triangle", "single-customer", "empty-route"],
)
def test_route_cost_includes_return_to_the_configured_depot(
    route: Route, expected_cost: int
) -> None:
    coordinates = [(3, 0), (0, 0), (0, 4)]

    assert route_cost(route, coordinates, depot=2) == expected_cost


def test_initial_solution_uses_first_fit_in_descending_demand_order() -> None:
    demands = [2, 7, 4, 2, 2, 3]
    fleet = build_initial_solution(
        vehicle_count=3, dimension=6, capacity=6, demands=demands, depot=2
    )

    assert fleet is not None
    assert [vehicle.route for vehicle in fleet] == [[3, 1], [6, 4], [5]]
    assert [vehicle.load for vehicle in fleet] == [6, 5, 2]


def test_initial_solution_fails_when_aggregate_capacity_cannot_be_packed() -> None:
    # The two vehicles can carry ten units in total, but each can fit only one customer.
    demands = [0, 3, 3, 3]

    fleet = build_initial_solution(
        vehicle_count=2, dimension=4, capacity=5, demands=demands, depot=1
    )

    assert fleet is None


def test_reverse_segment_reverses_both_endpoints_without_mutating_input() -> None:
    route = [2, 3, 4, 5, 6]

    reversed_route = reverse_segment(route, start=1, end=3)

    assert reversed_route == [2, 5, 4, 3, 6]
    assert route == [2, 3, 4, 5, 6]
