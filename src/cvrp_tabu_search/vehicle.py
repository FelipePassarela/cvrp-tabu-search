from dataclasses import field

from pydantic import PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass

from .route import Route


@validated_dataclass
class Vehicle:
    capacity: PositiveInt
    route: Route = field(default_factory=lambda: Route())
