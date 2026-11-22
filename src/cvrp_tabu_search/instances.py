from collections.abc import Iterable
from dataclasses import dataclass
from math import isfinite
from pathlib import Path
from typing import NamedTuple


class InstanceData(NamedTuple):
    vehicle_count: int
    dimension: int
    capacity: int
    coordinates: list[list[float]]
    demands: list[int]
    depot: int


@dataclass(frozen=True)
class Instance:
    name: str
    optimal_cost: int
    vehicle_count: int
    dimension: int
    capacity: int
    coordinates: list[list[float]]
    demands: list[int]
    depot: int


def load_default_instance() -> Instance:
    path = Path(__file__).with_name("data") / "A-n32-k5.vrp"
    return load_instance(path, optimal_cost=784)


def load_instance(path: Path, *, optimal_cost: int) -> Instance:
    instance = Instance(path.stem, optimal_cost, *read_instance(path))
    _validate_instance(instance)
    return instance


def read_instance(path: str | Path) -> InstanceData:
    with open(path, encoding="utf-8") as file:
        header, sections = _split_sections(file)

    if header.get("EDGE_WEIGHT_TYPE", "EUC_2D") != "EUC_2D":
        raise ValueError("Only EUC_2D edge weights are supported.")

    name = header.get("NAME", "k0")
    name_suffix = name.rsplit("-", 1)[-1]
    vehicle_count = int(name_suffix.rsplit("k", 1)[-1])
    dimension = int(header.get("DIMENSION", 0))
    capacity = int(header.get("CAPACITY", 0))

    coordinate_rows = _order_by_node_id(sections["NODE_COORD_SECTION"])
    demand_rows = _order_by_node_id(sections["DEMAND_SECTION"])
    coordinates = [[float(x), float(y)] for _, x, y in coordinate_rows]
    demands = [int(row[1]) for row in demand_rows]
    depot = _read_depot(sections["DEPOT_SECTION"])
    return InstanceData(
        vehicle_count=vehicle_count,
        dimension=dimension,
        capacity=capacity,
        coordinates=coordinates,
        demands=demands,
        depot=depot,
    )


def _validate_instance(instance: Instance) -> None:
    if instance.vehicle_count <= 0 or instance.capacity <= 0:
        raise ValueError("Vehicle count and capacity must be positive.")

    if instance.dimension <= 0 or not (
        len(instance.coordinates) == len(instance.demands) == instance.dimension
    ):
        raise ValueError("Coordinates and demands must match the declared dimension.")

    if not 1 <= instance.depot <= instance.dimension:
        raise ValueError("The depot must be a node in the instance.")

    if instance.demands[instance.depot - 1] != 0 or any(
        demand < 0 for demand in instance.demands
    ):
        raise ValueError(
            "Demands must be nonnegative and the depot demand must be zero."
        )

    if not all(isfinite(value) for point in instance.coordinates for value in point):
        raise ValueError("Coordinates must be finite.")


def _split_sections(
    lines: Iterable[str],
) -> tuple[dict[str, str], dict[str, list[list[str]]]]:
    header: dict[str, str] = {}
    sections: dict[str, list[list[str]]] = {
        "NODE_COORD_SECTION": [],
        "DEMAND_SECTION": [],
        "DEPOT_SECTION": [],
    }
    current_section = None

    for line in lines:
        text = line.strip()
        if text == "EOF":
            break

        if not text:
            continue

        if text in sections:
            current_section = text
        elif current_section is not None:
            sections[current_section].append(text.split())
        elif ":" in text:
            field, value = text.split(":", 1)
            header[field.strip()] = value.strip()

    return header, sections


def _read_depot(rows: Iterable[list[str]]) -> int:
    depot = None
    for row in rows:
        if row[0] == "-1":
            break

        if depot is not None:
            raise ValueError("Only one depot is supported.")

        depot = int(row[0])

    return 0 if depot is None else depot


def _order_by_node_id(rows: list[list[str]]) -> list[list[str]]:
    ordered = sorted(rows, key=lambda row: int(row[0]))
    if any(int(row[0]) != index for index, row in enumerate(ordered, start=1)):
        raise ValueError("Node IDs must be unique and consecutive, starting at 1.")

    return ordered
