import pytest

from cvrp_core.domain import Client, Depot
from cvrp_core.search.instance import Instance
from cvrp_core.search.stop_criteria import IterationStop, StagnationStop
from cvrp_core.search.tabu import TabuSearch, TabuSearchConfig, TabuTenure


def test_selects_the_best_feasible_neighbor_across_routes() -> None:
    instance = _make_instance(
        (1, 0), (2, 0), (9, 0), (10, 0), capacity=3, vehicle_count=2
    )
    config = TabuSearchConfig(iteration_stop=IterationStop(1))
    search = TabuSearch(config)

    result = search.solve(instance)

    assert result is not None
    assert result.completed_iterations == 1
    assert result.best_cost == 24
    routes = result.best_solution.routes
    visit_orders = [[client.id for client in route] for route in routes]
    assert visit_orders == [[2, 3], [4, 5]]


def test_accepts_a_tabu_inversion_when_it_improves_the_global_best() -> None:
    instance = _make_instance((1, 1), (-3, 2), (-1, -3), (2, 2), (3, -2), capacity=5)
    tenure = TabuTenure(minimum=5, maximum=5)
    config = TabuSearchConfig(iteration_stop=IterationStop(3), tenure=tenure)
    search = TabuSearch(config)

    result = search.solve(instance)

    # The third inversion reuses the tabu endpoints (2, 4) from the first.
    assert result is not None
    assert result.completed_iterations == 3
    assert result.best_cost == 19
    assert [client.id for client in result.best_solution.routes[0]] == [2, 5, 6, 4, 3]


@pytest.mark.parametrize(
    ("duration", "completed_iterations"),
    [(1, 1), (0, 4)],
    ids=["inverse-blocked", "memory-disabled"],
)
def test_tabu_tenure_controls_whether_the_only_inversion_can_be_repeated(
    duration: int, completed_iterations: int
) -> None:
    instance = _make_instance((1, 0), (2, 0), capacity=2)
    tenure = TabuTenure(minimum=duration, maximum=duration)
    config = TabuSearchConfig(iteration_stop=IterationStop(4), tenure=tenure)
    search = TabuSearch(config)

    result = search.solve(instance)

    assert result is not None
    assert result.completed_iterations == completed_iterations
    assert result.best_cost == 4
    assert [client.id for client in result.best_solution.routes[0]] == [2, 3]


def test_tabu_tenure_is_drawn_for_each_move_and_reproduced_by_seed() -> None:
    instance = _make_instance((1, 0), (2, 0), capacity=2)
    tenure = TabuTenure(minimum=0, maximum=1)
    config = TabuSearchConfig(iteration_stop=IterationStop(4), tenure=tenure)
    search = TabuSearch(config)
    seed = 1

    result = search.solve(instance, seed=seed)
    repeated_result = search.solve(instance, seed=seed)

    # Tenures 0, 0, 1 block the only inversion after the third move.
    assert result is not None
    assert result.completed_iterations == 3
    assert repeated_result == result


def test_stagnation_can_end_search_before_the_iteration_limit() -> None:
    instance = _make_instance((1, 0), (2, 0), capacity=2)
    config = TabuSearchConfig(
        iteration_stop=IterationStop(10),
        tenure=TabuTenure(minimum=0, maximum=0),
        stop_criteria=(StagnationStop(2),),
    )
    search = TabuSearch(config)

    result = search.solve(instance)

    assert result is not None
    assert result.completed_iterations == 2
    assert result.best_cost == 4


def test_zero_iterations_returns_the_initial_solution() -> None:
    instance = _make_instance(
        (1, 0), (2, 0), (9, 0), (10, 0), capacity=3, vehicle_count=2
    )
    config = TabuSearchConfig(iteration_stop=IterationStop(0))
    search = TabuSearch(config)

    result = search.solve(instance)

    assert result is not None
    assert result.completed_iterations == 0
    assert result.best_cost == 38


def test_search_stops_when_there_are_no_moves() -> None:
    instance = _make_instance((2, 0), capacity=1)
    config = TabuSearchConfig(iteration_stop=IterationStop(10))
    search = TabuSearch(config)

    result = search.solve(instance)

    assert result is not None
    assert result.completed_iterations == 0
    assert result.best_cost == 4


def test_search_returns_none_if_first_fit_cannot_place_all_clients() -> None:
    instance = _make_instance((1, 0), (2, 0), capacity=1)
    config = TabuSearchConfig(iteration_stop=IterationStop(10))
    search = TabuSearch(config)

    assert search.solve(instance) is None


def _make_instance(
    *client_positions: tuple[int, int], capacity: int, vehicle_count: int = 1
) -> Instance:
    depot = Depot(id=1, coord_x=0, coord_y=0)
    instance = Instance(depot=depot, capacity=capacity, vehicle_count=vehicle_count)
    for client_id, (x, y) in enumerate(client_positions, start=2):
        instance.add_client(Client(id=client_id, coord_x=x, coord_y=y, demand=1))
    return instance
