import subprocess
import sys
from pathlib import Path

_REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_cli_loads_the_bundled_instance_by_default(tmp_path: Path) -> None:
    result = _run_cli(tmp_path)

    assert result.returncode == 0, result.stderr
    assert "Client(id=2, demand=19, coord_x=96.0, coord_y=44.0)" in result.stdout


def test_cli_loads_the_requested_instance(tmp_path: Path) -> None:
    path = _REPOSITORY_ROOT / "benchmarks" / "general" / "F-n45-k4.vrp"

    result = _run_cli(tmp_path, str(path))

    assert result.returncode == 0, result.stderr
    assert "Client(id=45," in result.stdout


def test_cli_reports_a_missing_file(tmp_path: Path) -> None:
    result = _run_cli(tmp_path, "missing.vrp")

    assert result.returncode == 2
    assert "missing.vrp" in result.stderr


def _run_cli(cwd: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "cvrp_tabu_search", *arguments],
        cwd=cwd,
        capture_output=True,
        text=True,
        check=False,
    )
