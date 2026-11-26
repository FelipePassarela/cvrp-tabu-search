from cvrp_core.domain import Client, Depot, Route, Vehicle
from cvrp_core.search.solution import Solution
from cvrp_core.search.solution_evaluator import SolutionEvaluator


def test_evaluate_sums_rounded_legs_of_closed_routes() -> None:
    depot = Depot(id=1, coord_x=10, coord_y=-4)
    first = Client(id=2, demand=1, coord_x=12.5, coord_y=-4)
    second = Client(id=3, demand=1, coord_x=12.5, coord_y=-1)
    third = Client(id=4, demand=1, coord_x=10, coord_y=1)
    solution = Solution(
        vehicles=[
            Vehicle(capacity=5, route=Route(clients=[first, second])),
            Vehicle(capacity=5, route=Route(clients=[third])),
            Vehicle(capacity=5),
        ]
    )

    cost = SolutionEvaluator.evaluate(solution, depot)

    first_route_cost = 3 + 3 + 4
    second_route_cost = 5 + 5
    assert cost == first_route_cost + second_route_cost


def test_evaluate_returns_zero_for_an_empty_route() -> None:
    depot = Depot(id=1, coord_x=10, coord_y=-4)
    solution = Solution(vehicles=[Vehicle(capacity=5)])

    assert SolutionEvaluator.evaluate(solution, depot) == 0
