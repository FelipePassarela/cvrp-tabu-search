import pytest
from pydantic import ValidationError

from cvrp_tabu_search.domain import Client


@pytest.mark.parametrize("client_id", [0, -1])
def test_client_requires_a_positive_id(client_id: int) -> None:
    with pytest.raises(ValidationError) as error:
        Client(id=client_id, demand=5, coord_x=2, coord_y=3)

    assert error.value.errors()[0]["loc"] == ("id",)
