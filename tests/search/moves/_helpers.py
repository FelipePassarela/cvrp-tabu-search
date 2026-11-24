from cvrp_tabu_search.domain import Client, Route, Vehicle
from cvrp_tabu_search.search.solution import Solution


def make_client(client_id: int, demand: int = 1) -> Client:
    return Client(id=client_id, demand=demand, coord_x=0, coord_y=0)


def make_vehicle(*clients: Client, capacity: int = 100) -> Vehicle:
    return Vehicle(capacity=capacity, route=Route(clients=list(clients)))


def visit_orders(solution: Solution) -> list[list[int]]:
    return [[client.id for client in route.clients] for route in solution.routes]
