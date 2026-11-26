import pytest

from cvrp_core.domain import Route, Vehicle
from cvrp_core.search.solution import Solution


def test_solution_vehicle_at_returns_the_vehicle_at_that_position() -> None:
    first = Vehicle(capacity=10)
    second = Vehicle(capacity=20)
    solution = Solution(vehicles=[first, second])

    assert solution.vehicle_at(1) is second


@pytest.mark.parametrize("index", [-1, 1])
def test_solution_vehicle_at_rejects_indices_outside_the_fleet(index: int) -> None:
    solution = Solution(vehicles=[Vehicle(capacity=10)])

    with pytest.raises(IndexError, match=f"Route index {index} is out of range"):
        solution.vehicle_at(index)


def test_solution_exposes_vehicle_routes_in_fleet_order() -> None:
    first_route = Route()
    second_route = Route()
    first_vehicle = Vehicle(capacity=100, route=first_route)
    second_vehicle = Vehicle(capacity=100, route=second_route)
    solution = Solution(vehicles=[first_vehicle, second_vehicle])

    first_result, second_result = solution.routes

    assert first_result is first_route
    assert second_result is second_route


def test_solution_reflects_a_vehicle_route_replacement() -> None:
    vehicle = Vehicle(capacity=100)
    solution = Solution(vehicles=[vehicle])
    replacement = Route()

    vehicle.route = replacement

    assert solution.routes[0] is replacement


def test_empty_solution_has_no_vehicle_routes() -> None:
    solution = Solution()

    assert solution.vehicles == []
    assert solution.routes == []
