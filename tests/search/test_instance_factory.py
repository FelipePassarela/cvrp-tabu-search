from pathlib import Path
from textwrap import dedent

import pytest

from cvrp_tabu_search.domain import Client, Depot
from cvrp_tabu_search.search.instance_factory import load_instance

_REPOSITORY_ROOT = Path(__file__).resolve().parents[2]
_VRP_PATHS = sorted(_REPOSITORY_ROOT.glob("benchmarks/**/*.vrp")) + sorted(
    _REPOSITORY_ROOT.glob("src/**/data/*.vrp")
)

_REORDERED_VRP = dedent("""\
    NAME : reordered-k2
    TYPE : CVRP
    DIMENSION : 3
    EDGE_WEIGHT_TYPE : EUC_2D
    CAPACITY : 6
    NODE_COORD_SECTION
    12 -1.5 7.25
    3 -1.5 9
    8 2 9
    DEMAND_SECTION
    8 6
    12 4
    3 0
    DEPOT_SECTION
    3
    -1
    EOF
    """)


@pytest.mark.parametrize(
    "path", _VRP_PATHS, ids=lambda path: path.relative_to(_REPOSITORY_ROOT).as_posix()
)
def test_load_instance_reads_every_client_from_a_project_file(path: Path) -> None:
    header_lines = path.read_text(encoding="utf-8").splitlines()
    dimension_line = next(line for line in header_lines if line.startswith("DIMENSION"))
    node_count = int(dimension_line.split(":", 1)[1])

    instance = load_instance(path)

    assert len(instance.clients) == node_count - 1


def test_load_instance_keeps_the_depot_separate_from_clients(
    tmp_path: Path,
) -> None:
    path = tmp_path / "reordered.vrp"
    path.write_text(_REORDERED_VRP, encoding="utf-8-sig")
    expected_clients = {
        12: Client(id=12, demand=4, coord_x=-1.5, coord_y=7.25),
        8: Client(id=8, demand=6, coord_x=2, coord_y=9),
    }

    instance = load_instance(str(path))

    assert instance.depot == Depot(id=3, coord_x=-1.5, coord_y=9)
    assert instance.clients == expected_clients


@pytest.mark.parametrize(
    ("original", "replacement", "error_message"),
    [
        pytest.param(
            "EUC_2D", "EXPLICIT", "Only EUC_2D", id="unsupported-edge-weights"
        ),
        pytest.param(
            "DIMENSION : 3", "DIMENSION : 4", "declared dimension", id="wrong-dimension"
        ),
        pytest.param("CAPACITY : 6\n", "", "Missing CAPACITY", id="missing-capacity"),
        pytest.param(
            "reordered-k2", "reordered", "vehicle count", id="missing-vehicle-count"
        ),
        pytest.param(
            "NODE_COORD_SECTION",
            "",
            "Missing section NODE_COORD_SECTION",
            id="missing-coordinates",
        ),
        pytest.param(
            "12 -1.5 7.25",
            "12 -1.5",
            "Invalid row in NODE_COORD_SECTION",
            id="incomplete-coordinate-row",
        ),
        pytest.param("8 6", "12 6", "duplicate node ID", id="duplicate-demand-id"),
        pytest.param("8 6", "9 6", "same node IDs", id="mismatched-node-ids"),
        pytest.param("3 -1.5 9", "3 nan 9", "finite number", id="nonfinite-depot"),
        pytest.param(
            "3 0\nDEPOT_SECTION",
            "3 2\nDEPOT_SECTION",
            "demand zero",
            id="nonzero-depot-demand",
        ),
        pytest.param(
            "3\n-1\nEOF", "3\n8\n-1\nEOF", "one depot ID", id="multiple-depots"
        ),
    ],
)
def test_load_instance_rejects_a_malformed_file(
    tmp_path: Path, original: str, replacement: str, error_message: str
) -> None:
    path = tmp_path / "invalid.vrp"
    invalid_vrp = _REORDERED_VRP.replace(original, replacement)
    path.write_text(invalid_vrp, encoding="utf-8")

    with pytest.raises(ValueError, match=error_message):
        load_instance(path)
