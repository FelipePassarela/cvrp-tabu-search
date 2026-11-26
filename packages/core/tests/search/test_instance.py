import pytest

from cvrp_core.domain import Client, Depot
from cvrp_core.search.instance import Instance


@pytest.fixture
def instance() -> Instance:
    depot = Depot(id=1, coord_x=0, coord_y=0)
    return Instance(depot=depot, capacity=10, vehicle_count=1)


def test_add_client_stores_the_client_by_id(instance: Instance) -> None:
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)

    instance.add_client(client)

    assert instance.clients == {7: client}


def test_add_client_rejects_a_duplicate_id_and_preserves_the_original(
    instance: Instance,
) -> None:
    original = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(original)
    duplicate = Client(id=7, demand=8, coord_x=6, coord_y=1)

    with pytest.raises(ValueError, match="Client ID 7 already exists"):
        instance.add_client(duplicate)

    assert instance.clients == {7: original}


def test_mutating_the_clients_snapshot_preserves_the_registered_clients(
    instance: Instance,
) -> None:
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(client)

    snapshot = instance.clients
    snapshot.clear()

    assert instance.clients == {7: client}
