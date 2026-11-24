from cvrp_tabu_search.search.moves import ExchangeMove, InversionMove, ReallocationMove
from cvrp_tabu_search.search.moves.tabu_keys import TabuKey
from cvrp_tabu_search.search.solution import Solution
from cvrp_tabu_search.search.tabu_memory import TabuMemory

from ._helpers import make_client, make_vehicle


def test_inversion_blocks_reversing_the_same_endpoints() -> None:
    solution = Solution(
        vehicles=[make_vehicle(make_client(1), make_client(2), make_client(3))]
    )
    memory = TabuMemory[TabuKey]()
    inversion = InversionMove(route_index=0, start_index=0, end_index=2)
    keys = inversion.tabu_keys(solution)

    inversion.apply(solution)
    memory.register(keys.to_register, iteration=1, tenure=2)

    undo_keys = inversion.tabu_keys(solution)
    assert memory.is_tabu(undo_keys.to_check, iteration=2)


def test_reallocation_blocks_returning_to_the_source_at_a_different_position() -> None:
    solution = Solution(
        vehicles=[
            make_vehicle(make_client(1), make_client(2)),
            make_vehicle(make_client(3), make_client(4)),
        ]
    )
    memory = TabuMemory[TabuKey]()
    reallocation = ReallocationMove(
        source_route_index=0,
        source_client_index=1,
        target_route_index=1,
        target_client_index=0,
    )
    keys = reallocation.tabu_keys(solution)

    reallocation.apply(solution)
    memory.register(keys.to_register, iteration=1, tenure=2)

    return_move = ReallocationMove(1, 0, 0, 0)
    other_client_move = ReallocationMove(1, 1, 0, 0)
    return_keys = return_move.tabu_keys(solution).to_check
    other_client_keys = other_client_move.tabu_keys(solution).to_check
    assert memory.is_tabu(return_keys, iteration=2)
    assert not memory.is_tabu(other_client_keys, iteration=2)


def test_exchange_blocks_return_of_either_client() -> None:
    solution = Solution(
        vehicles=[
            make_vehicle(make_client(1), make_client(2)),
            make_vehicle(make_client(3), make_client(4)),
        ]
    )
    memory = TabuMemory[TabuKey]()
    exchange = ExchangeMove(
        first_route_index=0,
        first_client_index=0,
        second_route_index=1,
        second_client_index=0,
    )
    keys = exchange.tabu_keys(solution)

    exchange.apply(solution)
    memory.register(keys.to_register, iteration=1, tenure=2)

    returns_client_1 = ExchangeMove(0, 1, 1, 0)
    returns_client_3 = ExchangeMove(0, 0, 1, 1)
    client_1_keys = returns_client_1.tabu_keys(solution).to_check
    client_3_keys = returns_client_3.tabu_keys(solution).to_check
    assert memory.is_tabu(client_1_keys, iteration=2)
    assert memory.is_tabu(client_3_keys, iteration=2)
