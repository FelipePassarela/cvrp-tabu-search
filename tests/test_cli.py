import subprocess
import sys
from pathlib import Path


def test_cli_searches_the_bundled_instance_by_default(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "--max-iterations", "1", "--seed", "1")

    assert result.returncode == 0, result.stderr
    assert "Best cost: 2184" in result.stdout
    assert "Completed iterations: 1" in result.stdout
    assert "Route #1: 20 25 26 16 4" in result.stdout


def test_cli_searches_the_requested_instance_until_stagnation(tmp_path: Path) -> None:
    path = _write_two_client_instance(tmp_path, capacity=2)

    result = _run_cli(
        tmp_path,
        path.name,
        "--stagnation-limit",
        "2",
        "--tabu-tenure-min",
        "0",
        "--tabu-tenure-max",
        "0",
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout.splitlines() == [
        "Best cost: 4",
        "Completed iterations: 2",
        "Route #1: 2 3",
    ]


def test_cli_reports_a_missing_file(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "missing.vrp")

    assert result.returncode == 2
    assert "missing.vrp" in result.stderr


def test_cli_reports_an_invalid_tabu_tenure_range(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "--tabu-tenure-min", "5", "--tabu-tenure-max", "4")

    assert result.returncode == 2
    assert "Minimum tabu tenure must not exceed the maximum" in result.stderr


def test_cli_reports_failure_to_construct_an_initial_solution(tmp_path: Path) -> None:
    path = _write_two_client_instance(tmp_path, capacity=1)

    result = _run_cli(tmp_path, path.name)

    assert result.returncode == 1
    assert "could not construct an initial solution" in result.stderr


def _write_two_client_instance(directory: Path, *, capacity: int) -> Path:
    path = directory / "line-n3-k1.vrp"
    path.write_text(
        f"""\
        NAME : line-n3-k1
        CAPACITY : {capacity}
        NODE_COORD_SECTION
        1 0 0
        2 1 0
        3 2 0
        DEMAND_SECTION
        1 0
        2 1
        3 1
        DEPOT_SECTION
        1
        -1
        EOF
        """,
        encoding="utf-8",
    )
    return path


def _run_cli(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cvrp_tabu_search", *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
