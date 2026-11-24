from dataclasses import field

from pydantic.dataclasses import dataclass as validated_dataclass

from .instance import Client


@validated_dataclass
class Route:
    clients: list[Client] = field(default_factory=list)
