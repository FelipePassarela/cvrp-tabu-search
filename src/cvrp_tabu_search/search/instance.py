import copy
from dataclasses import field

from pydantic import PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..domain import Client


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
