import pytest
from pydantic import ValidationError

from cvrp_tabu_search.vehicle import Vehicle


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
