import os
import subprocess
import sys
from collections.abc import Sequence
from pathlib import Path

import pytest


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
