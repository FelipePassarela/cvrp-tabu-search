from cvrp_tabu_search.domain import Client, Depot
from cvrp_tabu_search.search.first_fit_solution_generator import (
    FirstFitSolutionGenerator,
)
from cvrp_tabu_search.search.instance import Instance


def test_first_fit_uses_descending_demand_and_the_first_vehicle_with_room() -> None:
    depot = Depot(id=1, coord_x=0, coord_y=0)
    instance = Instance(depot=depot, capacity=6, vehicle_count=3)
    for client_id, demand in [(9, 2), (5, 3), (3, 2), (7, 4)]:
        instance.add_client(Client(id=client_id, demand=demand, coord_x=0, coord_y=0))

    solution = FirstFitSolutionGenerator.generate(instance)

    assert solution is not None
    assert [[client.id for client in route] for route in solution.routes] == [
        [7, 3],
        [5, 9],
        [],
    ]
    assert [route.total_demand for route in solution.routes] == [6, 5, 0]


def test_first_fit_returns_none_when_no_vehicle_can_fit_the_last_client() -> None:
    depot = Depot(id=1, coord_x=0, coord_y=0)
    instance = Instance(depot=depot, capacity=5, vehicle_count=2)
    for client_id in (2, 3, 4):
        instance.add_client(Client(id=client_id, demand=3, coord_x=0, coord_y=0))

    assert FirstFitSolutionGenerator.generate(instance) is None
