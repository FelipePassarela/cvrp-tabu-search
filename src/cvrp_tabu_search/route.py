from dataclasses import field

from pydantic.dataclasses import dataclass as validated_dataclass

from .instance import Client


@validated_dataclass
class Route:
    clients: list[Client] = field(default_factory=list)

    def client_at(self, index: int) -> Client:
        self.check_client_index(index)
        return self.clients[index]

    def insert_client(self, index: int, client: Client) -> None:
        self.check_insertion_index(index)
        self.clients.insert(index, client)

    def remove_client(self, index: int) -> Client:
        self.check_client_index(index)
        return self.clients.pop(index)

    def replace_client(self, index: int, client: Client) -> None:
        self.check_client_index(index)
        self.clients[index] = client

    def reverse_segment(self, start_index: int, end_index: int) -> None:
        self.check_client_index(start_index)
        self.check_client_index(end_index)
        if start_index >= end_index:
            raise ValueError("An inversion must span at least two clients in order.")

        segment = slice(start_index, end_index + 1)
        self.clients[segment] = reversed(self.clients[segment])

    def check_distinct_from(self, other: "Route") -> None:
        if self.clients is other.clients:
            raise ValueError("The operation requires two distinct routes.")

    def check_client_index(self, index: int) -> None:
        if not 0 <= index < len(self.clients):
            raise IndexError(f"Client index {index} is out of range.")

    def check_insertion_index(self, index: int) -> None:
        if not 0 <= index <= len(self.clients):
            raise IndexError(f"Insertion index {index} is out of range.")

    @property
    def total_demand(self) -> int:
        return sum(client.demand for client in self.clients)
