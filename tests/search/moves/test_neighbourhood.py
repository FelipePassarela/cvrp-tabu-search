from cvrp_tabu_search.search.moves import (
    ExchangeMove,
    InversionMove,
    Neighbourhood,
    ReallocationMove,
)
from cvrp_tabu_search.search.solution import Solution

from ._helpers import make_client, make_vehicle, visit_orders


def test_generates_each_inversion_segment_once_without_changing_the_solution() -> None:
    solution = Solution(
        vehicles=[
            make_vehicle(make_client(1)),
            make_vehicle(make_client(2), make_client(3), make_client(4)),
            make_vehicle(),
        ]
    )

    moves = Neighbourhood.generate_moves(solution)
    inversions = [move for move in moves if isinstance(move, InversionMove)]

    assert inversions == [
        InversionMove(route_index=1, start_index=0, end_index=1),
        InversionMove(route_index=1, start_index=0, end_index=2),
        InversionMove(route_index=1, start_index=1, end_index=2),
    ]
    assert visit_orders(solution) == [[1], [2, 3, 4], []]


def test_generates_all_feasible_insertions_in_both_directions() -> None:
    first = make_vehicle(make_client(1, demand=2), make_client(2, demand=4), capacity=9)
    second = make_vehicle(
        make_client(3, demand=5), make_client(4, demand=3), capacity=10
    )
    solution = Solution(vehicles=[first, second])

    moves = Neighbourhood.generate_moves(solution)
    reallocations = [move for move in moves if isinstance(move, ReallocationMove)]

    assert reallocations == [
        ReallocationMove(0, 0, 1, 0),
        ReallocationMove(0, 0, 1, 1),
        ReallocationMove(0, 0, 1, 2),
        ReallocationMove(1, 1, 0, 0),
        ReallocationMove(1, 1, 0, 1),
        ReallocationMove(1, 1, 0, 2),
    ]


def test_skips_reallocations_that_would_empty_the_source_route() -> None:
    first = make_vehicle(make_client(1), capacity=1)
    second = make_vehicle(make_client(2), make_client(3), capacity=3)
    solution = Solution(vehicles=[first, second])

    moves = Neighbourhood.generate_moves(solution)
    reallocations = [move for move in moves if isinstance(move, ReallocationMove)]

    assert reallocations == []


def test_can_insert_into_an_empty_route_at_position_zero() -> None:
    source = make_vehicle(make_client(1), make_client(2, demand=2))
    target = make_vehicle(capacity=1)
    solution = Solution(vehicles=[source, target])

    moves = Neighbourhood.generate_moves(solution)
    reallocations = [move for move in moves if isinstance(move, ReallocationMove)]

    assert reallocations == [
        ReallocationMove(
            source_route_index=0,
            source_client_index=0,
            target_route_index=1,
            target_client_index=0,
        )
    ]


def test_generates_each_exchange_once_and_checks_both_capacities() -> None:
    first = make_vehicle(make_client(1, demand=2), make_client(2, demand=4), capacity=6)
    second = make_vehicle(
        make_client(3, demand=4),
        make_client(4, demand=2),
        make_client(5, demand=6),
        capacity=12,
    )
    solution = Solution(vehicles=[first, second])

    moves = Neighbourhood.generate_moves(solution)
    exchanges = [move for move in moves if isinstance(move, ExchangeMove)]

    assert exchanges == [
        ExchangeMove(
            first_route_index=0,
            first_client_index=0,
            second_route_index=1,
            second_client_index=1,
        ),
        ExchangeMove(
            first_route_index=0,
            first_client_index=1,
            second_route_index=1,
            second_client_index=0,
        ),
    ]


def test_empty_solution_returns_an_empty_move_iterator() -> None:
    moves = Neighbourhood.generate_moves(Solution())

    assert iter(moves) is moves
    assert list(moves) == []
