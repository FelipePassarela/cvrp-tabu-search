from dataclasses import field

from pydantic import PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass

from .instance import Client
from .route import Route


@validated_dataclass
class Vehicle:
    capacity: PositiveInt
    route: Route = field(default_factory=lambda: Route())

    def insert_client(self, index: int, client: Client) -> None:
        new_demand = self.route.total_demand + client.demand
        self.check_capacity(new_demand)
        self.route.insert_client(index, client)

    def remove_client(self, index: int) -> Client:
        return self.route.remove_client(index)

    def exchange_clients(self, index: int, other: "Vehicle", other_index: int) -> None:
        route = self.route
        route.check_distinct_from(other.route)
        outgoing = route.client_at(index)
        incoming = other.route.client_at(other_index)

        demand_delta = incoming.demand - outgoing.demand
        self.check_capacity(route.total_demand + demand_delta)
        other.check_capacity(other.route.total_demand - demand_delta)

        route.replace_client(index, incoming)
        other.route.replace_client(other_index, outgoing)

    def check_capacity(self, demand: int) -> None:
        if demand > self.capacity:
            raise ValueError(
                f"Route demand {demand} exceeds vehicle capacity {self.capacity}."
            )
