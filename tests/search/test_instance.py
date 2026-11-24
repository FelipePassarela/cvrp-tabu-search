import pytest

from cvrp_tabu_search.domain import Client
from cvrp_tabu_search.search.instance import Instance


def test_add_client_stores_the_client_by_id() -> None:
    instance = Instance()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)

    instance.add_client(client)

    assert instance.clients == {7: client}


def test_add_client_rejects_a_duplicate_id_and_preserves_the_original() -> None:
    instance = Instance()
    original = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(original)
    duplicate = Client(id=7, demand=8, coord_x=6, coord_y=1)

    with pytest.raises(ValueError, match="Client ID 7 already exists"):
        instance.add_client(duplicate)

    assert instance.clients == {7: original}


def test_mutating_the_clients_snapshot_preserves_the_registered_clients() -> None:
    instance = Instance()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(client)

    snapshot = instance.clients
    snapshot.clear()

    assert instance.clients == {7: client}
