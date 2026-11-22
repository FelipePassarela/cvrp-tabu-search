from __future__ import annotations

import csv
from collections.abc import Iterable, Iterator, Sequence
from typing import TYPE_CHECKING, NamedTuple

import matplotlib.pyplot as plt

from .instances import Instance
from .search import SearchHistory, SearchParameters

if TYPE_CHECKING:
    from .experiment import Run

RUN_HEADER = (
    "instance",
    "repetition",
    "seed",
    "tabu_tenure_min",
    "tabu_tenure_max",
    "max_iterations",
    "stagnation_limit",
    "optimal_cost",
    "best_cost",
    "time_to_best_s",
    "total_time_s",
    "time_to_target_s",
)
HISTORY_HEADER = ("iteration", "best_cost", "elapsed_time_s", "current_cost")

type CsvValue = str | int | float | None


class TargetMeasurement(NamedTuple):
    total_time_s: float
    time_to_target_s: float | None


def generate_reports(
    instance: Instance,
    parameters: SearchParameters,
    runs: Sequence[Run],
    *,
    prefix: str = "",
) -> None:
    name = f"{prefix}{instance.name}"
    run_rows = _run_rows(instance, parameters, runs)
    write_csv(f"runs_{name}.csv", RUN_HEADER, run_rows)

    best_run = min(runs, key=lambda run: run.cost)
    best_history = best_run.history
    write_csv(f"history_{name}.csv", HISTORY_HEADER, best_history[1:])

    measurements = [
        TargetMeasurement(run.total_time_s, run.time_to_target_s) for run in runs
    ]
    generate_plots(
        instance.name, instance.optimal_cost, best_history, measurements, prefix=prefix
    )


def _run_rows(
    instance: Instance, parameters: SearchParameters, runs: Iterable[Run]
) -> Iterator[list[CsvValue]]:
    for repetition, run in enumerate(runs, start=1):
        yield [
            instance.name,
            repetition,
            run.seed,
            *parameters.tabu_tenure,
            parameters.max_iterations,
            parameters.stagnation_limit,
            instance.optimal_cost,
            run.cost,
            run.time_to_best_s,
            run.total_time_s,
            run.time_to_target_s,
        ]


def write_csv(
    path: str, header: Iterable[str], rows: Iterable[Iterable[CsvValue]]
) -> None:
    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)


def generate_plots(
    instance_name: str,
    optimal_cost: int,
    best_history: SearchHistory,
    measurements: Sequence[TargetMeasurement],
    *,
    prefix: str = "",
) -> None:
    plt.style.use("default")
    name = f"{prefix}{instance_name}"
    _plot_convergence(
        instance_name, optimal_cost, best_history, f"convergence_{name}.png"
    )
    _plot_time_to_target(instance_name, optimal_cost, measurements, f"ttt_{name}.png")


def _plot_convergence(
    instance_name: str, optimal_cost: int, history: SearchHistory, path: str
) -> None:
    iterations: list[int] = []
    costs: list[int] = []

    # The first history entry is the initial solution.
    for iteration, _, _, current_cost in history[1:]:
        iterations.append(iteration)
        costs.append(current_cost)

    figure, axes = plt.subplots(figsize=(9, 5))
    axes.plot(iterations, costs, color="tab:blue", label="Iteration cost")
    axes.axhline(
        optimal_cost,
        color="tab:orange",
        linestyle="--",
        label=f"Optimum: {optimal_cost}",
    )
    axes.set_title(f"Tabu search convergence — {instance_name}")
    axes.set_xlabel("Iteration")
    axes.set_ylabel("Total cost")
    axes.legend()

    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def _plot_time_to_target(
    instance_name: str,
    optimal_cost: int,
    measurements: Sequence[TargetMeasurement],
    path: str,
) -> None:
    times, percentages, hits = _time_to_target_curve(measurements)
    total = len(measurements)

    figure, axes = plt.subplots(figsize=(9, 5))
    axes.step(
        times,
        percentages,
        where="post",
        color="tab:blue",
        label=f"Target {optimal_cost}: {hits} of {total}",
    )
    axes.set_title(f"Time to target — {instance_name}")
    axes.set_xlabel("Elapsed time (s)")
    axes.set_ylabel("Runs that reached the target (%)")
    axes.set_ylim(-4, 104)
    axes.set_yticks([0, 25, 50, 75, 100])
    axes.legend()

    figure.tight_layout()
    figure.savefig(path, dpi=200)
    plt.close(figure)


def _time_to_target_curve(
    measurements: Sequence[TargetMeasurement],
) -> tuple[list[float], list[float], int]:
    target_times: list[float] = []
    longest_run = 0.0
    for total_time, target_time in measurements:
        longest_run = max(longest_run, total_time)
        if target_time is not None:
            target_times.append(target_time)

    target_times.sort()
    total = len(measurements)
    times: list[float] = [0]
    percentages: list[float] = [0]
    for hits, time in enumerate(target_times, start=1):
        times.append(time)
        percentages.append(100 * hits / total)

    # Extend the curve to the end of the observation window.
    times.append(longest_run)
    percentages.append(percentages[-1])
    return times, percentages, len(target_times)
