from pathlib import Path

import typer
from pydantic import ValidationError

from cvrp_core.search.instance import Instance
from cvrp_core.search.instance_factory import load_instance
from cvrp_core.search.stop_criteria import IterationStop, StagnationStop
from cvrp_core.search.tabu import (
    DEFAULT_TABU_TENURE,
    TabuSearch,
    TabuSearchConfig,
    TabuTenure,
)

from .args import (
    DEFAULT_INSTANCE_PATH,
    InstancePath,
    IterationLimit,
    RandomSeed,
    StagnationLimit,
    TabuTenureMaximum,
    TabuTenureMinimum,
)
from .output import print_search_result

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
    config = _build_search_config(
        max_iterations, stagnation_limit, tabu_tenure_min, tabu_tenure_max
    )
    search = TabuSearch(config)
    instance = _read_instance(path)
    result = search.solve(instance, seed=seed)

    if result is None:
        typer.echo(
            "First Fit Decreasing could not construct an initial solution.", err=True
        )
        raise typer.Exit(code=1)

    print_search_result(result, instance.optimal_cost)


def _read_instance(path: Path) -> Instance:
    try:
        return load_instance(path)
    except (OSError, ValueError) as error:
        raise typer.BadParameter(str(error), param_hint="PATH") from error


def _build_search_config(
    max_iterations: int, stagnation_limit: int, tenure_minimum: int, tenure_maximum: int
) -> TabuSearchConfig:
    iteration_stop = IterationStop(max_iterations=max_iterations)
    stagnation_stop = StagnationStop(stagnation_limit=stagnation_limit)
    try:
        tenure = TabuTenure(minimum=tenure_minimum, maximum=tenure_maximum)
    except ValidationError as error:
        raise typer.BadParameter(
            "Must be at least --tabu-tenure-min.", param_hint="--tabu-tenure-max"
        ) from error

    return TabuSearchConfig(
        iteration_stop=iteration_stop, tenure=tenure, stop_criteria=(stagnation_stop,)
    )


if __name__ == "__main__":
    app()
