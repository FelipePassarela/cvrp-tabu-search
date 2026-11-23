from itertools import product
from math import isfinite
from pathlib import Path
from typing import Annotated

import typer

from .experiments.calibration import (
    CALIBRATION_TIME_LIMIT_S,
    CalibrationError,
    load_calibration_instances,
    run_calibration,
)
from .experiments.reports import DEFAULT_OUTPUT_DIR
from .experiments.runner import run_baseline_experiment, run_tabu_search_experiment
from .instances import Instance, load_default_instance, load_instance
from .search.shared import DEFAULT_TABU_TENURE, SearchParameters, TabuTenure

app = typer.Typer(help="Run the CVRP tabu search experiments.", no_args_is_help=True)


def _validate_time_limit(value: float | None) -> float | None:
    if value is not None and not isfinite(value):
        raise typer.BadParameter("Must be a finite number of seconds.")
    return value


InstancePath = Annotated[
    Path | None,
    typer.Option(
        "--instance",
        exists=True,
        dir_okay=False,
        readable=True,
        help="Path to a CVRP instance file. Defaults to the bundled A-n32-k5 instance.",
    ),
]
TargetCost = Annotated[
    int | None,
    typer.Option(
        min=0, help="Known optimal cost for --instance, used as the reporting target."
    ),
]
IterationLimit = Annotated[
    int, typer.Option(min=0, help="Maximum number of iterations per run.")
]
StagnationLimit = Annotated[
    int,
    typer.Option(min=1, help="Stop after this many iterations without improvement."),
]
_time_limit_option = typer.Option(
    min=0.0,
    callback=_validate_time_limit,
    help="Time limit in seconds per run, checked before each neighborhood scan.",
)
TimeLimit = Annotated[float | None, _time_limit_option]
CalibrationTimeLimit = Annotated[float, _time_limit_option]
TabuTenureMinimum = Annotated[
    int, typer.Option(min=0, help="Minimum number of iterations a move stays tabu.")
]
TabuTenureMaximum = Annotated[
    int, typer.Option(min=0, help="Maximum number of iterations a move stays tabu.")
]
OutputDirectory = Annotated[
    Path,
    typer.Option(
        file_okay=False,
        writable=True,
        show_default=True,
        help="Parent directory for timestamped report folders.",
    ),
]
BenchmarksDirectory = Annotated[
    Path,
    typer.Option(
        exists=True,
        file_okay=False,
        readable=True,
        help="Directory containing A-n80-k10.vrp and B-n78-k10.vrp.",
    ),
]
TenureLevels = tuple[int, int, int]
CalibrationMinimums = Annotated[
    TenureLevels,
    typer.Option("--tabu-tenure-min", min=0, help="Three minimum durations."),
]
CalibrationMaximums = Annotated[
    TenureLevels,
    typer.Option("--tabu-tenure-max", min=0, help="Three maximum durations."),
]
CalibrationJobs = Annotated[
    int, typer.Option(min=1, help="Maximum number of calibration runs in parallel.")
]


@app.command("baseline")
def baseline_command(
    instance: InstancePath = None,
    target_cost: TargetCost = None,
    max_iterations: IterationLimit = 10,
    stagnation_limit: StagnationLimit = 10,
    output_dir: OutputDirectory = DEFAULT_OUTPUT_DIR,
    tabu_tenure_min: TabuTenureMinimum = DEFAULT_TABU_TENURE.minimum,
    tabu_tenure_max: TabuTenureMaximum = DEFAULT_TABU_TENURE.maximum,
    time_limit: TimeLimit = None,
) -> None:
    """Run the baseline with reversals within each route."""
    tenure = _resolve_tabu_tenure(tabu_tenure_min, tabu_tenure_max)
    problem = _resolve_instance(instance, target_cost)
    parameters = SearchParameters(
        max_iterations, stagnation_limit, tabu_tenure=tenure, time_limit_s=time_limit
    )
    if not run_baseline_experiment(problem, parameters, output_dir=output_dir):
        raise typer.Exit(code=1)


@app.command("tabu-search")
def tabu_search_command(
    instance: InstancePath = None,
    target_cost: TargetCost = None,
    max_iterations: IterationLimit = 60,
    stagnation_limit: StagnationLimit = 30,
    output_dir: OutputDirectory = DEFAULT_OUTPUT_DIR,
    tabu_tenure_min: TabuTenureMinimum = DEFAULT_TABU_TENURE.minimum,
    tabu_tenure_max: TabuTenureMaximum = DEFAULT_TABU_TENURE.maximum,
    time_limit: TimeLimit = None,
    phases: Annotated[
        bool,
        typer.Option(
            "--phases/--no-phases",
            help="Use intensification and diversification (disable for ablation).",
        ),
    ] = True,
) -> None:
    """Run the search with inter-route moves, intensification and diversification."""
    tenure = _resolve_tabu_tenure(tabu_tenure_min, tabu_tenure_max)
    problem = _resolve_instance(instance, target_cost)
    parameters = SearchParameters(
        max_iterations, stagnation_limit, tabu_tenure=tenure, time_limit_s=time_limit
    )
    if not run_tabu_search_experiment(
        problem, parameters, output_dir=output_dir, use_phases=phases
    ):
        raise typer.Exit(code=1)


@app.command("calibrate")
def calibrate_command(
    benchmarks_dir: BenchmarksDirectory = Path("benchmarks/selected"),
    output_dir: OutputDirectory = DEFAULT_OUTPUT_DIR,
    time_limit: CalibrationTimeLimit = CALIBRATION_TIME_LIMIT_S,
    tenure_minimums: CalibrationMinimums = (1, 3, 6),
    tenure_maximums: CalibrationMaximums = (7, 11, 15),
    jobs: CalibrationJobs = 1,
) -> None:
    """Compare tabu tenure bounds on the three calibration instances."""
    tenures = _resolve_calibration_tenures(tenure_minimums, tenure_maximums)
    try:
        instances = load_calibration_instances(benchmarks_dir)
    except (OSError, ValueError, IndexError) as error:
        raise typer.BadParameter(str(error), param_hint="--benchmarks-dir") from error

    try:
        run_calibration(
            instances,
            tenures,
            time_limit_s=time_limit,
            output_dir=output_dir,
            jobs=jobs,
        )
    except (CalibrationError, OSError) as error:
        typer.echo(str(error), err=True)
        raise typer.Exit(code=1) from error


def _resolve_calibration_tenures(
    minimums: TenureLevels, maximums: TenureLevels
) -> list[TabuTenure]:
    for levels, option in (
        (minimums, "--tabu-tenure-min"),
        (maximums, "--tabu-tenure-max"),
    ):
        if len(set(levels)) != len(levels):
            raise typer.BadParameter("Use three distinct values.", param_hint=option)

    largest_minimum = max(minimums)
    if min(maximums) < largest_minimum:
        raise typer.BadParameter(
            f"All values must be at least {largest_minimum}.",
            param_hint="--tabu-tenure-max",
        )

    return [
        TabuTenure(minimum, maximum) for minimum, maximum in product(minimums, maximums)
    ]


def _resolve_tabu_tenure(minimum: int, maximum: int) -> TabuTenure:
    if minimum > maximum:
        raise typer.BadParameter(
            "Must be at least --tabu-tenure-min.", param_hint="--tabu-tenure-max"
        )
    return TabuTenure(minimum, maximum)


def _resolve_instance(path: Path | None, target_cost: int | None) -> Instance:
    if path is None:
        if target_cost is not None:
            raise typer.BadParameter("Requires --instance.", param_hint="--target-cost")
        return load_default_instance()

    if target_cost is None:
        raise typer.BadParameter(
            "Required with --instance.", param_hint="--target-cost"
        )

    try:
        return load_instance(path, optimal_cost=target_cost)
    except (OSError, ValueError, IndexError) as error:
        raise typer.BadParameter(
            f"Could not read {path}: {error}", param_hint="--instance"
        ) from error
