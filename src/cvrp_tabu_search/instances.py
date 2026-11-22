from collections.abc import Iterable
from dataclasses import dataclass
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
    name = "A-n32-k5"
    optimal_cost = 784
    path = Path(__file__).with_name("data") / f"{name}.vrp"
    return Instance(name, optimal_cost, *read_instance(path))


def read_instance(path: str | Path) -> InstanceData:
    with open(path, encoding="utf-8") as file:
        header, sections = _split_sections(file)

    name = header.get("NAME", "k0")
    name_suffix = name.rsplit("-", 1)[-1]
    vehicle_count = int(name_suffix.rsplit("k", 1)[-1])
    dimension = int(header.get("DIMENSION", 0))
    capacity = int(header.get("CAPACITY", 0))

    coordinates = [[float(x), float(y)] for _, x, y in sections["NODE_COORD_SECTION"]]
    demands = [int(row[1]) for row in sections["DEMAND_SECTION"]]
    depot = _read_depot(sections["DEPOT_SECTION"])
    return InstanceData(
        vehicle_count=vehicle_count,
        dimension=dimension,
        capacity=capacity,
        coordinates=coordinates,
        demands=demands,
        depot=depot,
    )


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
        if "EOF" in line:
            break

        text = line.strip()
        if text in sections:
            current_section = text
        elif current_section is not None:
            sections[current_section].append(text.split())
        elif ":" in text:
            field, value = text.split(":", 1)
            header[field.strip()] = value.strip()

    return header, sections


def _read_depot(rows: Iterable[list[str]]) -> int:
    depot = 0
    for row in rows:
        if "-1" in row:
            break
        depot = int(row[0])

    return depot
