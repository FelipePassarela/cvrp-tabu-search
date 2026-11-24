import pytest

from cvrp_tabu_search.instance import Client, Instance
from cvrp_tabu_search.route import Route


def test_route_preserves_the_order_of_client_visits() -> None:
    clients = [
        Client(id=7, demand=5, coord_x=2, coord_y=3),
        Client(id=12, demand=8, coord_x=6, coord_y=1),
        Client(id=3, demand=4, coord_x=4, coord_y=7),
    ]

    route = Route(clients=clients)

    assert [client.id for client in route] == [7, 12, 3]


def test_route_length_counts_its_clients() -> None:
    route = Route()
    assert len(route) == 0

    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    route.insert_client(0, client)

    assert len(route) == 1


def test_each_empty_route_has_its_own_client_list() -> None:
    route = Route()
    other_route = Route()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)

    route.insert_client(0, client)

    assert route.clients == [client]
    assert other_route.clients == []


def test_route_references_the_client_registered_in_the_instance() -> None:
    instance = Instance()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(client)

    route = Route(clients=[instance.clients[7]])

    assert route.client_at(0) is client


@pytest.mark.parametrize("index", [-1, 1])
def test_route_client_at_rejects_indices_outside_the_route(index: int) -> None:
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    route = Route(clients=[client])

    with pytest.raises(IndexError, match=f"Client index {index} is out of range"):
        route.client_at(index)


def test_route_inserts_a_client_at_the_requested_position() -> None:
    first = Client(id=7, demand=5, coord_x=2, coord_y=3)
    last = Client(id=12, demand=8, coord_x=6, coord_y=1)
    inserted = Client(id=3, demand=4, coord_x=4, coord_y=7)
    route = Route(clients=[first, last])

    route.insert_client(1, inserted)

    assert route.clients == [first, inserted, last]


@pytest.mark.parametrize("index", [-1, 2])
def test_route_rejects_an_invalid_insertion_without_changes(index: int) -> None:
    original = Client(id=7, demand=5, coord_x=2, coord_y=3)
    inserted = Client(id=3, demand=4, coord_x=4, coord_y=7)
    route = Route(clients=[original])

    with pytest.raises(IndexError, match=f"Insertion index {index} is out of range"):
        route.insert_client(index, inserted)

    assert route.clients == [original]


@pytest.mark.parametrize("index", [-1, 1])
def test_route_rejects_an_invalid_removal_without_changes(index: int) -> None:
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    route = Route(clients=[client])

    with pytest.raises(IndexError, match=f"Client index {index} is out of range"):
        route.remove_client(index)

    assert route.clients == [client]


@pytest.mark.parametrize("index", [-1, 1])
def test_route_rejects_an_invalid_replacement_without_changes(index: int) -> None:
    original = Client(id=7, demand=5, coord_x=2, coord_y=3)
    replacement = Client(id=3, demand=4, coord_x=4, coord_y=7)
    route = Route(clients=[original])

    with pytest.raises(IndexError, match=f"Client index {index} is out of range"):
        route.replace_client(index, replacement)

    assert route.clients == [original]


def test_route_rejects_reversing_a_segment_with_reversed_endpoints() -> None:
    first = Client(id=7, demand=5, coord_x=2, coord_y=3)
    second = Client(id=12, demand=8, coord_x=6, coord_y=1)
    route = Route(clients=[first, second])

    with pytest.raises(ValueError, match="at least two clients in order"):
        route.reverse_segment(1, 0)

    assert route.clients == [first, second]
