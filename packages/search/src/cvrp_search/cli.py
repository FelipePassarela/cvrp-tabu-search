from pathlib import Path

import typer
from pydantic import ValidationError

from cvrp_core.search.instance import Instance
from cvrp_core.search.instance_factory import load_instance
from cvrp_core.search.stop_criteria import IterationStop, StagnationStop
from cvrp_core.search.tabu_search import SearchResult, TabuSearch
from cvrp_core.search.tabu_tenure import DEFAULT_TABU_TENURE, TabuTenure

from .cli_args import (
    DEFAULT_INSTANCE_PATH,
    InstancePath,
    IterationLimit,
    RandomSeed,
    StagnationLimit,
    TabuTenureMaximum,
    TabuTenureMinimum,
)

app = typer.Typer(add_completion=False)


@app.command()
def run(
    path: InstancePath = DEFAULT_INSTANCE_PATH,
    max_iterations: IterationLimit = 60,
    stagnation_limit: StagnationLimit = 30,
    tabu_tenure_min: TabuTenureMinimum = DEFAULT_TABU_TENURE.minimum,
    tabu_tenure_max: TabuTenureMaximum = DEFAULT_TABU_TENURE.maximum,
    seed: RandomSeed = None,
) -> None:
    """Run tabu search on a CVRP instance."""
    search = _build_search(
        max_iterations, stagnation_limit, tabu_tenure_min, tabu_tenure_max
    )
    instance = _read_instance(path)
    result = search.solve(instance, seed=seed)

    if result is None:
        typer.echo(
            "First Fit Decreasing could not construct an initial solution.", err=True
        )
        raise typer.Exit(code=1)

    _print_result(result, instance.optimal_cost)


def _read_instance(path: Path) -> Instance:
    try:
        return load_instance(path)
    except (OSError, ValueError) as error:
        raise typer.BadParameter(str(error), param_hint="PATH") from error


def _build_search(
    max_iterations: int, stagnation_limit: int, tenure_minimum: int, tenure_maximum: int
) -> TabuSearch:
    iteration_stop = IterationStop(max_iterations=max_iterations)
    stagnation_stop = StagnationStop(stagnation_limit=stagnation_limit)
    try:
        tenure = TabuTenure(minimum=tenure_minimum, maximum=tenure_maximum)
    except ValidationError as error:
        raise typer.BadParameter(
            "Must be at least --tabu-tenure-min.", param_hint="--tabu-tenure-max"
        ) from error

    return TabuSearch(
        iteration_stop=iteration_stop, tenure=tenure, stop_criteria=(stagnation_stop,)
    )


def _print_result(result: SearchResult, optimal_cost: int | None) -> None:
    print(_format_cost_summary(result.best_cost, optimal_cost))
    print(f"Completed iterations: {result.completed_iterations}")
    for vehicle_number, route in enumerate(result.best_solution.routes, start=1):
        if route:
            client_ids = " ".join(str(client.id) for client in route)
            print(f"Route #{vehicle_number}: {client_ids}")


def _format_cost_summary(best_cost: int, optimal_cost: int | None) -> str:
    best_cost_summary = f"Best cost: {best_cost}"
    if optimal_cost is None:
        return f"{best_cost_summary} | Optimal cost: N/A | Gap: N/A"

    cost_difference = best_cost - optimal_cost
    absolute_gap = abs(cost_difference)
    relative_gap = cost_difference / optimal_cost
    return (
        f"{best_cost_summary} | Optimal cost: {optimal_cost}"
        f" | Gap: {absolute_gap} ({relative_gap:.2%})"
    )


if __name__ == "__main__":
    app()
