import csv
import os
import subprocess
import sys
from pathlib import Path

import pytest


def _run_command(
    command: str, working_directory: Path
) -> subprocess.CompletedProcess[str]:
    executable_name = f"{command}.exe" if os.name == "nt" else command
    executable = Path(sys.executable).with_name(executable_name)
    environment = os.environ | {
        "MPLBACKEND": "Agg",
        "MPLCONFIGDIR": str(working_directory.parent / "matplotlib"),
    }
    return subprocess.run(
        [str(executable)],
        cwd=working_directory,
        env=environment,
        capture_output=True,
        encoding="utf-8",
        timeout=30,
        check=False,
    )


def _read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as report:
        return list(csv.DictReader(report))


@pytest.mark.parametrize(
    ("command", "prefix", "expected_cost", "iteration_limit", "stagnation_limit"),
    [("cvrp-baseline", "", 1470, 10, 10), ("cvrp-tabu-search", "tabu_", 915, 60, 30)],
    ids=["baseline", "advanced"],
)
def test_installed_command_generates_reports_outside_the_repository(
    tmp_path: Path,
    command: str,
    prefix: str,
    expected_cost: int,
    iteration_limit: int,
    stagnation_limit: int,
) -> None:
    working_directory = tmp_path / "output"
    working_directory.mkdir()

    result = _run_command(command, working_directory)

    assert result.returncode == 0, result.stderr
    repetitions = list(range(1, 6))
    output = result.stdout.splitlines()
    assert len(output) == len(repetitions)
    for repetition, line in zip(repetitions, output, strict=True):
        assert line.startswith(f"Run {repetition}: cost {expected_cost} | time ")

    suffix = f"{prefix}A-n32-k5"
    runs_path = working_directory / f"runs_{suffix}.csv"
    history_path = working_directory / f"history_{suffix}.csv"
    plots = [
        working_directory / f"{kind}_{suffix}.png" for kind in ("convergence", "ttt")
    ]
    assert set(working_directory.iterdir()) == {runs_path, history_path, *plots}
    for plot in plots:
        assert plot.read_bytes().startswith(b"\x89PNG\r\n\x1a\n"), plot

    runs = _read_csv(runs_path)
    assert [int(run["seed"]) for run in runs] == repetitions
    assert {int(run["best_cost"]) for run in runs} == {expected_cost}
    assert {int(run["max_iterations"]) for run in runs} == {iteration_limit}
    assert {int(run["stagnation_limit"]) for run in runs} == {stagnation_limit}

    history = _read_csv(history_path)
    assert [int(row["iteration"]) for row in history] == list(
        range(1, len(history) + 1)
    )
    assert int(history[-1]["best_cost"]) == expected_cost
