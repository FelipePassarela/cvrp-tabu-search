from collections.abc import Iterator, Sequence
from itertools import product
from pathlib import Path
from sys import maxsize

from ..instances import Instance, load_default_instance, load_instance
from ..search.shared import SearchParameters, TabuTenure
from .reports import CsvValue, write_csv
from .reports.directory import create_report_directory
from .runner import run_tabu_search_repetition

CALIBRATION_TIME_LIMIT_S = 180.0
CALIBRATION_SEED = 1
CALIBRATION_HEADER = (
    "instance",
    "tabu_tenure_min",
    "tabu_tenure_max",
    "seed",
    "optimal_cost",
    "time_limit_s",
    "total_time_s",
    "best_cost",
)


class CalibrationError(RuntimeError):
    pass


def load_calibration_instances(benchmarks_dir: Path) -> tuple[Instance, ...]:
    return (
        load_default_instance(),
        load_instance(benchmarks_dir / "A-n80-k10.vrp", optimal_cost=1763),
        load_instance(benchmarks_dir / "B-n78-k10.vrp", optimal_cost=1221),
    )


def run_calibration(
    instances: Sequence[Instance],
    tenures: Sequence[TabuTenure],
    *,
    time_limit_s: float,
    output_dir: Path,
) -> None:
    report_path = create_report_directory(output_dir) / "calibration.csv"
    print(f"Calibration table: {report_path}", flush=True)
    rows = _calibration_rows(instances, tenures, time_limit_s)
    write_csv(report_path, CALIBRATION_HEADER, rows, flush_rows=True)


def _calibration_rows(
    instances: Sequence[Instance], tenures: Sequence[TabuTenure], time_limit_s: float
) -> Iterator[tuple[CsvValue, ...]]:
    total_trials = len(instances) * len(tenures)
    for index, (instance, tenure) in enumerate(product(instances, tenures), start=1):
        print(
            f"[{index}/{total_trials}] {instance.name}: tabu tenure "
            f"[{tenure.minimum}, {tenure.maximum}]",
            flush=True,
        )
        yield _run_trial(instance, tenure, time_limit_s)


def _run_trial(
    instance: Instance, tenure: TabuTenure, time_limit_s: float
) -> tuple[CsvValue, ...]:
    # Keep both iteration limits out of reach so the time budget governs the trial.
    parameters = SearchParameters(
        max_iterations=maxsize,
        stagnation_limit=maxsize,
        tabu_tenure=tenure,
        time_limit_s=time_limit_s,
    )
    run = run_tabu_search_repetition(instance, parameters, seed=CALIBRATION_SEED)
    if run is None:
        raise CalibrationError(
            f"Could not build a feasible initial solution for {instance.name}."
        )

    return (
        instance.name,
        tenure.minimum,
        tenure.maximum,
        run.seed,
        instance.optimal_cost,
        time_limit_s,
        run.total_time_s,
        run.cost,
    )
