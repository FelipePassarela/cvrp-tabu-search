import re
from collections.abc import Iterable, Iterator
from pathlib import Path

from ..domain import Client, Depot
from .instance import Instance

type _VrpHeader = dict[str, str]
type _VrpSections = dict[str, list[str]]
type _RawNodeRow = tuple[int, list[str]]
type _CoordinatesByNode = dict[int, tuple[float, float]]
type _DemandsByNode = dict[int, int]

_COORDINATE_SECTION = "NODE_COORD_SECTION"
_DEMAND_SECTION = "DEMAND_SECTION"
_DEPOT_SECTION = "DEPOT_SECTION"


def load_instance(path: str | Path) -> Instance:
    with Path(path).open(encoding="utf-8-sig") as file:
        header, sections = _split_sections(file)

    if header.get("EDGE_WEIGHT_TYPE", "EUC_2D") != "EUC_2D":
        raise ValueError("Only EUC_2D edge weights are supported.")

    coordinates = _read_coordinates(sections)
    demands = _read_demands(sections)
    depot_id = _read_depot_id(sections)
    _validate_nodes(header, coordinates, demands, depot_id)
    return _build_instance(header, coordinates, demands, depot_id)


def _split_sections(lines: Iterable[str]) -> tuple[_VrpHeader, _VrpSections]:
    header: _VrpHeader = {}
    sections: _VrpSections = {}
    current_section = None

    for line in lines:
        text = line.strip()
        if text == "EOF":
            break
        if not text:
            continue

        if text.endswith("_SECTION") and text.isidentifier():
            if text in sections:
                raise ValueError(f"Duplicate section {text}.")
            current_section = []
            sections[text] = current_section
        elif current_section is not None:
            current_section.append(text)
        elif ":" in text:
            field, value = text.split(":", 1)
            header[field.strip()] = value.strip()

    return header, sections


def _read_coordinates(sections: _VrpSections) -> _CoordinatesByNode:
    rows = _node_rows(sections, _COORDINATE_SECTION, value_count=2)
    return {node_id: (float(x), float(y)) for node_id, (x, y) in rows}


def _read_demands(sections: _VrpSections) -> _DemandsByNode:
    rows = _node_rows(sections, _DEMAND_SECTION, value_count=1)
    return {node_id: int(demand) for node_id, (demand,) in rows}


def _section_rows(sections: _VrpSections, section: str) -> list[str]:
    if section not in sections:
        raise ValueError(f"Missing section {section}.")
    return sections[section]


def _node_rows(
    sections: _VrpSections, section: str, value_count: int
) -> Iterator[_RawNodeRow]:
    seen_nodes: set[int] = set()
    for row in _section_rows(sections, section):
        identifier, *values = row.split()
        if len(values) != value_count:
            raise ValueError(f"Invalid row in {section}: {row!r}.")

        node_id = int(identifier)
        if node_id <= 0 or node_id in seen_nodes:
            raise ValueError(f"Invalid or duplicate node ID {node_id} in {section}.")

        seen_nodes.add(node_id)
        yield node_id, values


def _read_depot_id(sections: _VrpSections) -> int:
    rows = _section_rows(sections, _DEPOT_SECTION)
    tokens = " ".join(rows).split()
    if len(tokens) != 2 or tokens[1] != "-1":
        raise ValueError("DEPOT_SECTION must contain one depot ID followed by -1.")
    return int(tokens[0])


def _validate_nodes(
    header: _VrpHeader,
    coordinates: _CoordinatesByNode,
    demands: _DemandsByNode,
    depot_id: int,
) -> None:
    if coordinates.keys() != demands.keys():
        raise ValueError("Coordinates and demands must use the same node IDs.")

    declared_dimension = header.get("DIMENSION")
    if declared_dimension is not None and int(declared_dimension) != len(coordinates):
        raise ValueError("The node count must match the declared dimension.")

    if demands.get(depot_id) != 0:
        raise ValueError("The depot must be a node with demand zero.")


def _build_instance(
    header: _VrpHeader,
    coordinates: _CoordinatesByNode,
    demands: _DemandsByNode,
    depot_id: int,
) -> Instance:
    depot_x, depot_y = coordinates[depot_id]
    depot = Depot(id=depot_id, coord_x=depot_x, coord_y=depot_y)
    instance = Instance(
        depot=depot,
        capacity=_read_capacity(header),
        vehicle_count=_read_vehicle_count(header),
    )
    for node_id, (x, y) in coordinates.items():
        if node_id == depot_id:
            continue

        client = Client(id=node_id, demand=demands[node_id], coord_x=x, coord_y=y)
        instance.add_client(client)

    return instance


def _read_capacity(header: _VrpHeader) -> int:
    declared_capacity = header.get("CAPACITY")
    if declared_capacity is None:
        raise ValueError("Missing CAPACITY field.")
    return int(declared_capacity)


def _read_vehicle_count(header: _VrpHeader) -> int:
    fleet_suffix = re.search(r"-k(\d+)$", header.get("NAME", ""))
    if fleet_suffix is None:
        raise ValueError("NAME must end in -kN to specify the vehicle count.")
    return int(fleet_suffix.group(1))
