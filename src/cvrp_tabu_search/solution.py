from dataclasses import field

from pydantic.dataclasses import dataclass as validated_dataclass

from .route import Route
from .vehicle import Vehicle


@validated_dataclass
class Solution:
    vehicles: list[Vehicle] = field(default_factory=list)

    @property
    def routes(self) -> list[Route]:
        return [vehicle.route for vehicle in self.vehicles]
