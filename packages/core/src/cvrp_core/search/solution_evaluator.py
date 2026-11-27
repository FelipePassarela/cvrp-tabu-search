from math import hypot

from ..domain import Depot, Route
from .solution import Solution


class SolutionEvaluator:
    @staticmethod
    def evaluate(solution: Solution, depot: Depot) -> int:
        """Sum the EUC_2D costs of the routes, including departure and return legs."""
        route_costs = (
            SolutionEvaluator._route_cost(route, depot)
            for route in solution.routes
            if route
        )
        return sum(route_costs)

    @staticmethod
    def calculate_relative_gap(best_cost: int, optimal_cost: int) -> float:
        """Return the signed relative gap to a positive reference cost."""
        cost_difference = best_cost - optimal_cost
        return cost_difference / optimal_cost

    @staticmethod
    def _route_cost(route: Route, depot: Depot) -> int:
        depot_location = (depot.coord_x, depot.coord_y)
        cost = 0
        previous = depot_location
        for client in route:
            location = (client.coord_x, client.coord_y)
            cost += SolutionEvaluator._edge_cost(previous, location)
            previous = location

        return cost + SolutionEvaluator._edge_cost(previous, depot_location)

    @staticmethod
    def _edge_cost(start: tuple[float, float], end: tuple[float, float]) -> int:
        delta_x = end[0] - start[0]
        delta_y = end[1] - start[1]
        distance = hypot(delta_x, delta_y)
        return int(distance + 0.5)
