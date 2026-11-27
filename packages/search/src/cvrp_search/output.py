from cvrp_core.search.solution import Solution
from cvrp_core.search.solution_evaluator import SolutionEvaluator
from cvrp_core.search.tabu_search import SearchResult


def print_search_result(result: SearchResult, optimal_cost: int | None) -> None:
    print(_format_cost_summary(result.best_cost, optimal_cost))
    print(f"Completed iterations: {result.completed_iterations}")
    _print_routes(result.best_solution)


def _format_cost_summary(best_cost: int, optimal_cost: int | None) -> str:
    best_cost_summary = f"Best cost: {best_cost}"
    if optimal_cost is None:
        return f"{best_cost_summary} | Optimal cost: N/A | Gap: N/A"

    absolute_gap = abs(best_cost - optimal_cost)
    relative_gap = SolutionEvaluator.calculate_relative_gap(best_cost, optimal_cost)
    return (
        f"{best_cost_summary} | Optimal cost: {optimal_cost}"
        f" | Gap: {absolute_gap} ({relative_gap:.2%})"
    )


def _print_routes(solution: Solution) -> None:
    for vehicle_number, route in enumerate(solution.routes, start=1):
        if route:
            client_ids = " ".join(str(client.id) for client in route)
            print(f"Route #{vehicle_number}: {client_ids}")
