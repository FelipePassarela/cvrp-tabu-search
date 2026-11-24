from dataclasses import field

from pydantic.dataclasses import dataclass as validated_dataclass

from ..domain import Route, Vehicle


@validated_dataclass
class Solution:
    vehicles: list[Vehicle] = field(default_factory=list)

    def vehicle_at(self, index: int) -> Vehicle:
        if not 0 <= index < len(self.vehicles):
            raise IndexError(f"Route index {index} is out of range.")
        return self.vehicles[index]

    def vehicles_with_distinct_routes(
        self, first_route_index: int, second_route_index: int
    ) -> tuple[Vehicle, Vehicle]:
        first = self.vehicle_at(first_route_index)
        second = self.vehicle_at(second_route_index)
        first.route.check_distinct_from(second.route)
        return first, second

    @property
    def routes(self) -> list[Route]:
        return [vehicle.route for vehicle in self.vehicles]
