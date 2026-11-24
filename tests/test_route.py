from cvrp_tabu_search.instance import Client, Instance
from cvrp_tabu_search.route import Route


def test_route_preserves_the_order_of_client_visits() -> None:
    clients = [
        Client(id=7, demand=5, coord_x=2, coord_y=3),
        Client(id=12, demand=8, coord_x=6, coord_y=1),
        Client(id=3, demand=4, coord_x=4, coord_y=7),
    ]

    route = Route(clients=clients)

    assert [client.id for client in route.clients] == [7, 12, 3]


def test_each_empty_route_has_its_own_client_list() -> None:
    route = Route()
    other_route = Route()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)

    route.clients.append(client)

    assert route.clients == [client]
    assert other_route.clients == []


def test_route_references_the_client_registered_in_the_instance() -> None:
    instance = Instance()
    client = Client(id=7, demand=5, coord_x=2, coord_y=3)
    instance.add_client(client)

    route = Route(clients=[instance.clients[7]])

    assert route.clients[0] is client
