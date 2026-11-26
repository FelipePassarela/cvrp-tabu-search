import pytest
from pydantic import ValidationError

from cvrp_core.domain import Client, Vehicle


def test_each_vehicle_starts_with_its_own_empty_route() -> None:
    first_vehicle = Vehicle(capacity=100)
    second_vehicle = Vehicle(capacity=100)

    assert first_vehicle.route.clients == []
    assert second_vehicle.route.clients == []
    assert first_vehicle.route is not second_vehicle.route


@pytest.mark.parametrize("capacity", [0, -1])
def test_vehicle_requires_positive_capacity(capacity: int) -> None:
    with pytest.raises(ValidationError) as error:
        Vehicle(capacity=capacity)

    assert error.value.errors()[0]["loc"] == ("capacity",)


def test_vehicle_inserts_a_client_up_to_its_capacity() -> None:
    vehicle = Vehicle(capacity=5)
    existing = Client(id=7, demand=2, coord_x=2, coord_y=3)
    inserted = Client(id=12, demand=3, coord_x=6, coord_y=1)
    vehicle.insert_client(0, existing)

    vehicle.insert_client(0, inserted)

    assert vehicle.route.clients == [inserted, existing]
    assert vehicle.route.total_demand == 5


def test_vehicle_rejects_an_insertion_that_exceeds_its_capacity() -> None:
    vehicle = Vehicle(capacity=4)
    existing = Client(id=7, demand=2, coord_x=2, coord_y=3)
    candidate = Client(id=12, demand=3, coord_x=6, coord_y=1)
    vehicle.insert_client(0, existing)

    with pytest.raises(ValueError, match="exceeds vehicle capacity"):
        vehicle.insert_client(1, candidate)

    assert vehicle.route.clients == [existing]


def test_vehicle_removes_and_returns_the_client_at_the_requested_position() -> None:
    vehicle = Vehicle(capacity=5)
    remaining = Client(id=7, demand=2, coord_x=2, coord_y=3)
    selected = Client(id=12, demand=3, coord_x=6, coord_y=1)
    vehicle.insert_client(0, selected)
    vehicle.insert_client(1, remaining)

    removed = vehicle.remove_client(0)

    assert removed is selected
    assert vehicle.route.clients == [remaining]
    assert vehicle.route.total_demand == 2


def test_vehicle_rejects_exchange_when_routes_share_their_client_list() -> None:
    first = Vehicle(capacity=5)
    second = Vehicle(capacity=5)
    client = Client(id=7, demand=2, coord_x=2, coord_y=3)
    first.insert_client(0, client)
    second.route.clients = first.route.clients

    with pytest.raises(ValueError, match="two distinct routes"):
        first.exchange_clients(0, second, 0)

    assert first.route.clients == [client]
    assert second.route.clients == [client]
