from cvrp_tabu_search.route import Route
from cvrp_tabu_search.solution import Solution
from cvrp_tabu_search.vehicle import Vehicle


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
