from typing import cast

import pytest
from pydantic import ValidationError

from cvrp_tabu_search.moves import InversionMove
from cvrp_tabu_search.solution import Solution

from ._helpers import make_client, make_vehicle, visit_orders


def test_inversion_reverses_only_the_selected_segment() -> None:
    first = make_vehicle(*(make_client(client_id) for client_id in (1, 2, 3, 4, 5)))
    second = make_vehicle(make_client(6))
    solution = Solution(vehicles=[first, second])
    move = InversionMove(route_index=0, start_index=1, end_index=3)

    move.apply(solution)

    assert visit_orders(solution) == [[1, 4, 3, 2, 5], [6]]


@pytest.mark.parametrize(
    "route_index,error_type",
    [
        pytest.param(-1, "greater_than_equal", id="negative"),
        pytest.param(-10, "greater_than_equal", id="negative"),
        pytest.param(1.1, "int_from_float", id="float"),
    ],
)
def test_move_construction_requires_a_nonnegative_integer_index(
    route_index: object, error_type: str
) -> None:
    with pytest.raises(ValidationError) as error:
        InversionMove(route_index=cast(int, route_index), start_index=0, end_index=1)

    detail = error.value.errors()[0]
    assert detail["loc"] == ("route_index",)
    assert detail["type"] == error_type


@pytest.mark.parametrize("start_index,end_index", [(2, 1), (1, 1)])
def test_inversion_rejects_an_invalid_segment_without_changing_the_route(
    start_index: int, end_index: int
) -> None:
    vehicle = make_vehicle(make_client(1), make_client(2), make_client(3))
    solution = Solution(vehicles=[vehicle])
    move = InversionMove(route_index=0, start_index=start_index, end_index=end_index)

    with pytest.raises(ValueError, match="at least two clients"):
        move.apply(solution)

    assert visit_orders(solution) == [[1, 2, 3]]
