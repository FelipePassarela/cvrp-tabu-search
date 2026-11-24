import copy
from dataclasses import field

from pydantic import FiniteFloat, PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass


@validated_dataclass(frozen=True)
class Client:
    id: PositiveInt
    demand: PositiveInt
    coord_x: FiniteFloat
    coord_y: FiniteFloat


@validated_dataclass(frozen=True)
class Instance:
    _clients: dict[PositiveInt, Client] = field(default_factory=dict)

    def add_client(self, client: Client) -> None:
        if client.id in self._clients:
            raise ValueError(f"Client ID {client.id} already exists.")
        self._clients[client.id] = client

    @property
    def clients(self) -> dict[PositiveInt, Client]:
        return copy.copy(self._clients)
