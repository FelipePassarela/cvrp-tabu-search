import pytest
from pydantic import ValidationError

from cvrp_tabu_search.moves import ReallocationMove
from cvrp_tabu_search.solution import Solution

from ._helpers import make_client, make_vehicle, visit_orders


def test_reallocation_rejects_a_negative_insertion_index_on_creation() -> None:
    with pytest.raises(ValidationError) as error:
        ReallocationMove(
            source_route_index=0,
            source_client_index=0,
            target_route_index=1,
            target_client_index=-1,
        )

    assert error.value.errors()[0]["loc"] == ("target_client_index",)


def test_reallocation_inserts_the_same_client_at_the_target_position() -> None:
    client = make_client(2, demand=3)
    source = make_vehicle(make_client(1), client)
    target = make_vehicle(
        make_client(3, demand=2), make_client(4, demand=2), capacity=7
    )
    solution = Solution(vehicles=[source, target])
    move = ReallocationMove(
        source_route_index=0,
        source_client_index=1,
        target_route_index=1,
        target_client_index=1,
    )

    move.apply(solution)

    assert visit_orders(solution) == [[1], [3, 2, 4]]
    assert target.route.clients[1] is client
    assert target.route.total_demand == target.capacity


def test_reallocation_can_append_and_leave_the_source_empty() -> None:
    source = make_vehicle(make_client(1))
    target = make_vehicle(make_client(2))
    solution = Solution(vehicles=[source, target])
    move = ReallocationMove(
        source_route_index=0,
        source_client_index=0,
        target_route_index=1,
        target_client_index=1,
    )

    move.apply(solution)

    assert visit_orders(solution) == [[], [2, 1]]


def test_reallocation_rejects_an_overloaded_target_without_changes() -> None:
    source = make_vehicle(make_client(1, demand=3))
    target = make_vehicle(make_client(2, demand=2), capacity=4)
    solution = Solution(vehicles=[source, target])
    move = ReallocationMove(
        source_route_index=0,
        source_client_index=0,
        target_route_index=1,
        target_client_index=0,
    )

    with pytest.raises(ValueError, match="exceeds vehicle capacity"):
        move.apply(solution)

    assert visit_orders(solution) == [[1], [2]]


def test_reallocation_rejects_a_source_that_would_remain_over_capacity() -> None:
    relocated = make_client(1, demand=2)
    remaining = make_client(2, demand=5)
    source = make_vehicle(relocated, remaining, capacity=4)
    target = make_vehicle(make_client(3), capacity=6)
    solution = Solution(vehicles=[source, target])
    move = ReallocationMove(
        source_route_index=0,
        source_client_index=0,
        target_route_index=1,
        target_client_index=1,
    )

    with pytest.raises(ValueError, match="Route demand 5 exceeds vehicle capacity 4"):
        move.apply(solution)

    assert visit_orders(solution) == [[1, 2], [3]]
