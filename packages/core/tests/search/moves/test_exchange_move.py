import pytest

from cvrp_core.search.moves import ExchangeMove
from cvrp_core.search.solution import Solution

from ._helpers import make_client, make_vehicle, visit_orders


def test_exchange_succeeds_when_either_reallocation_would_overload() -> None:
    first_client = make_client(1, demand=4)
    second_client = make_client(4, demand=2)
    first = make_vehicle(first_client, make_client(2, demand=3), capacity=7)
    second = make_vehicle(make_client(3), second_client, capacity=5)
    solution = Solution(vehicles=[first, second])
    move = ExchangeMove(
        first_route_index=0,
        first_client_index=0,
        second_route_index=1,
        second_client_index=1,
    )

    move.apply(solution)

    assert visit_orders(solution) == [[4, 2], [3, 1]]
    assert first.route.clients[0] is second_client
    assert second.route.clients[1] is first_client
    assert first.route.total_demand == 5
    assert second.route.total_demand == second.capacity


@pytest.mark.parametrize("first_route,second_route", [(0, 1), (1, 0)])
def test_exchange_rejects_an_overload_on_either_side_before_changing_routes(
    first_route: int, second_route: int
) -> None:
    solution = Solution(
        vehicles=[
            make_vehicle(make_client(1, demand=4), capacity=4),
            make_vehicle(make_client(2, demand=2), capacity=3),
        ]
    )
    move = ExchangeMove(
        first_route_index=first_route,
        first_client_index=0,
        second_route_index=second_route,
        second_client_index=0,
    )

    with pytest.raises(ValueError, match="exceeds vehicle capacity"):
        move.apply(solution)

    assert visit_orders(solution) == [[1], [2]]
