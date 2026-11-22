from pathlib import Path
from textwrap import dedent

import pytest

from cvrp_tabu_search.instances import load_default_instance, read_instance


def test_read_instance_parses_header_and_sections(tmp_path: Path) -> None:
    path = tmp_path / "example.vrp"
    path.write_text(
        dedent(
            """
            NAME : example-n3-k2
            COMMENT: The name provides the fleet size
            DIMENSION: 3
            CAPACITY : 7
            NODE_COORD_SECTION
              1 3.5 -1
              2 0 0
              3 0 4.25
            DEMAND_SECTION
              1 3
              2 0
              3 4
            DEPOT_SECTION
              2
              -1
            EOF
            NODE_COORD_SECTION
              1 99 99
            """
        ),
        encoding="utf-8",
    )

    instance = read_instance(path)

    assert instance == (2, 3, 7, [[3.5, -1.0], [0.0, 0.0], [0.0, 4.25]], [3, 0, 4], 2)


def test_default_instance_loads_outside_the_repository(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)

    instance = load_default_instance()

    assert instance.name == "A-n32-k5"
    assert instance.optimal_cost == 784
    assert (instance.vehicle_count, instance.dimension, instance.capacity) == (
        5,
        32,
        100,
    )
    assert instance.depot == 1
    assert instance.demands[instance.depot - 1] == 0
    assert len(instance.coordinates) == len(instance.demands) == instance.dimension


@pytest.mark.parametrize("collection", ["general", "selected"])
def test_benchmark_collection_is_readable(collection: str) -> None:
    repository = Path(__file__).resolve().parents[1]
    instances = sorted((repository / "benchmarks" / collection).glob("*.vrp"))
    assert instances, f"No benchmark instances found in {collection}"

    for path in instances:
        vehicle_count, dimension, capacity, coordinates, demands, depot = read_instance(
            path
        )
        assert vehicle_count > 0 and capacity > 0, path
        assert len(coordinates) == len(demands) == dimension, path
        assert 1 <= depot <= dimension, path
        assert demands[depot - 1] == 0, path
