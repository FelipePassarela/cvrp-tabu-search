import csv
import os
import random
import subprocess
import sys
from collections.abc import Iterator, Sequence
from pathlib import Path
from textwrap import dedent

import matplotlib
import pytest
from typer.testing import CliRunner

from cvrp_tabu_search.cli import app


def _run_process(
    arguments: Sequence[str], working_directory: Path
) -> subprocess.CompletedProcess[str]:
    environment = os.environ | {
        "MPLBACKEND": "Agg",
        "MPLCONFIGDIR": str(working_directory.parent / "matplotlib"),
        "PYTHONUTF8": "1",
    }
    return subprocess.run(
        arguments,
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


@pytest.fixture
def report_directory(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[Path]:
    output = tmp_path / "output"
    output.mkdir()
    monkeypatch.chdir(output)
    random_state = random.getstate()
    try:
        with matplotlib.rc_context():
            yield output
    finally:
        random.setstate(random_state)


@pytest.mark.parametrize(
    (
        "subcommand",
        "prefix",
        "expected_cost",
        "iteration_limit",
        "stagnation_limit",
    ),
    [
        ("baseline", "", 1470, 10, 10),
        ("tabu-search", "tabu_", 915, 60, 30),
    ],
    ids=["baseline", "advanced"],
)
def test_subcommand_generates_reports_outside_the_repository(
    report_directory: Path,
    subcommand: str,
    prefix: str,
    expected_cost: int,
    iteration_limit: int,
    stagnation_limit: int,
) -> None:
    result = CliRunner().invoke(app, [subcommand])

    assert result.exit_code == 0, result.output
    repetitions = list(range(1, 6))
    output = result.output.splitlines()
    assert len(output) == len(repetitions)
    for repetition, line in zip(repetitions, output, strict=True):
        assert line.startswith(f"Run {repetition}: cost {expected_cost} | time ")

    suffix = f"{prefix}A-n32-k5"
    runs_path = report_directory / f"runs_{suffix}.csv"
    history_path = report_directory / f"history_{suffix}.csv"
    plots = [
        report_directory / f"{kind}_{suffix}.png" for kind in ("convergence", "ttt")
    ]
    assert set(report_directory.iterdir()) == {runs_path, history_path, *plots}
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


@pytest.fixture
def rectangle_path(tmp_path: Path) -> Path:
    instance = tmp_path / "rectangle instance.vrp"
    instance.write_text(
        dedent(
            """
            NAME: rectangle-n4-k1
            DIMENSION: 4
            CAPACITY: 3
            NODE_COORD_SECTION
            1 0 0
            2 4 0
            3 0 3
            4 4 3
            DEMAND_SECTION
            1 0
            2 1
            3 1
            4 1
            DEPOT_SECTION
            1
            -1
            EOF
            """
        ),
        encoding="utf-8",
    )
    return instance


@pytest.mark.parametrize(
    ("subcommand", "prefix", "iterations", "expected_cost"),
    [
        ("baseline", "", 0, 18),
        ("tabu-search", "tabu_", 1, 14),
    ],
    ids=["baseline", "advanced"],
)
def test_cli_uses_custom_instance_target_and_search_limits(
    report_directory: Path,
    rectangle_path: Path,
    subcommand: str,
    prefix: str,
    iterations: int,
    expected_cost: int,
) -> None:
    arguments = [
        subcommand,
        "--instance",
        str(rectangle_path),
        "--target-cost",
        "14",
        "--max-iterations",
        str(iterations),
        "--stagnation-limit",
        "2",
    ]

    result = CliRunner().invoke(app, arguments)

    assert result.exit_code == 0, result.output
    runs = _read_csv(report_directory / f"runs_{prefix}{rectangle_path.stem}.csv")
    assert len(runs) == 5
    assert {run["optimal_cost"] for run in runs} == {"14"}
    assert {run["best_cost"] for run in runs} == {str(expected_cost)}
    assert {run["max_iterations"] for run in runs} == {str(iterations)}
    assert {run["stagnation_limit"] for run in runs} == {"2"}
    history = _read_csv(report_directory / f"history_{prefix}{rectangle_path.stem}.csv")
    assert len(history) == iterations
    assert (runs[0]["time_to_target_s"] != "") is (expected_cost == 14)


@pytest.mark.parametrize(
    "command",
    [
        [
            str(
                Path(sys.executable).with_name(
                    "cvrp.exe" if os.name == "nt" else "cvrp"
                )
            )
        ],
        [sys.executable, "-m", "cvrp_tabu_search"],
    ],
    ids=["console-script", "package-module"],
)
def test_entrypoint_exposes_the_cli(tmp_path: Path, command: list[str]) -> None:
    result = _run_process([*command, "--help"], tmp_path)

    assert result.returncode == 0, result.stderr
    assert "baseline" in result.stdout
    assert "tabu-search" in result.stdout
    assert list(tmp_path.iterdir()) == []


def test_subcommand_help_lists_the_available_options() -> None:
    result = CliRunner().invoke(app, ["baseline", "--help"])

    assert result.exit_code == 0
    for option in (
        "--instance",
        "--target-cost",
        "--max-iterations",
        "--stagnation-limit",
    ):
        assert option in result.output


def test_custom_instance_requires_a_reference_cost(
    rectangle_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["baseline", "--instance", str(rectangle_path)])

    assert result.exit_code == 2
    assert "--target-cost" in result.output
    assert list(tmp_path.iterdir()) == [rectangle_path]


@pytest.mark.parametrize(
    ("options", "error_option"),
    [
        (["--target-cost", "20"], "--target-cost"),
        (["--target-cost", "-1"], "--target-cost"),
        (["--max-iterations", "-1"], "--max-iterations"),
        (["--stagnation-limit", "0"], "--stagnation-limit"),
        (["--instance", "missing.vrp", "--target-cost", "14"], "--instance"),
    ],
    ids=[
        "target-without-instance",
        "negative-target",
        "negative-limit",
        "zero-stagnation",
        "missing-file",
    ],
)
def test_invalid_options_report_usage_errors(
    options: list[str],
    error_option: str,
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.chdir(tmp_path)

    result = CliRunner().invoke(app, ["tabu-search", *options])

    assert result.exit_code == 2
    assert error_option in result.output
    assert list(tmp_path.iterdir()) == []


def test_cli_rejects_an_incomplete_instance_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    path = Path("incomplete.vrp")
    path.write_text(
        "NAME: incomplete-n2-k1\nDIMENSION: 2\nCAPACITY: 1\nEOF\n", encoding="utf-8"
    )

    result = CliRunner().invoke(
        app, ["baseline", "--instance", str(path), "--target-cost", "14"]
    )

    assert result.exit_code == 2
    assert "declared dimension" in result.output
    assert list(tmp_path.iterdir()) == [tmp_path / path]


def test_cli_returns_failure_when_the_initial_fleet_is_infeasible(
    rectangle_path: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    contents = rectangle_path.read_text(encoding="utf-8")
    rectangle_path.write_text(
        contents.replace("CAPACITY: 3", "CAPACITY: 1"), encoding="utf-8"
    )

    result = CliRunner().invoke(
        app, ["baseline", "--instance", str(rectangle_path), "--target-cost", "14"]
    )

    assert result.exit_code == 1
    assert "Could not build a feasible initial solution." in result.output
    assert list(tmp_path.iterdir()) == [rectangle_path]
