import pytest
from pydantic import ValidationError

from cvrp_tabu_search.moves import ExchangeMove, InversionMove, Move, ReallocationMove
from cvrp_tabu_search.route import Route
from cvrp_tabu_search.solution import Solution
from cvrp_tabu_search.vehicle import Vehicle

from ._helpers import make_client, make_vehicle, visit_orders


@pytest.mark.parametrize(
    "move,error_message",
    [
        pytest.param(InversionMove(2, 0, 1), "Route index", id="missing-route"),
        pytest.param(InversionMove(0, 0, 2), "Client index", id="inversion-end"),
        pytest.param(
            ReallocationMove(0, 2, 1, 0), "Client index", id="reallocation-source"
        ),
        pytest.param(
            ReallocationMove(0, 0, 1, 2), "Insertion index", id="reallocation-target"
        ),
        pytest.param(ExchangeMove(0, 0, 1, 1), "Client index", id="exchange-target"),
    ],
)
def test_out_of_range_moves_leave_the_solution_intact(
    move: Move, error_message: str
) -> None:
    solution = Solution(
        vehicles=[
            make_vehicle(make_client(1), make_client(2)),
            make_vehicle(make_client(3)),
        ]
    )

    with pytest.raises(IndexError, match=error_message):
        move.apply(solution)

    assert visit_orders(solution) == [[1, 2], [3]]


@pytest.mark.parametrize("move_type", [ReallocationMove, ExchangeMove])
def test_inter_route_moves_require_different_route_indices_on_creation(
    move_type: type[ReallocationMove] | type[ExchangeMove],
) -> None:
    with pytest.raises(ValidationError, match="two distinct routes"):
        move_type(0, 0, 0, 1)


@pytest.mark.parametrize(
    "move",
    [
        pytest.param(ReallocationMove(0, 0, 1, 1), id="reallocation"),
        pytest.param(ExchangeMove(0, 0, 1, 1), id="exchange"),
    ],
)
def test_inter_route_moves_reject_vehicles_with_a_shared_route(move: Move) -> None:
    shared_route = Route(clients=[make_client(1), make_client(2)])
    solution = Solution(
        vehicles=[
            Vehicle(capacity=10, route=shared_route),
            Vehicle(capacity=10, route=shared_route),
        ]
    )

    with pytest.raises(ValueError, match="two distinct routes"):
        move.apply(solution)

    assert visit_orders(solution) == [[1, 2], [1, 2]]
