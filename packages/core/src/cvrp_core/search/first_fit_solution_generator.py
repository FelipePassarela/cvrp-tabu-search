from ..domain import Vehicle
from .instance import Instance
from .solution import Solution


class FirstFitSolutionGenerator:
    @staticmethod
    def generate(instance: Instance) -> Solution | None:
        """Pack clients into the instance's fleet in descending demand order.

        Return None if any client cannot be assigned to a vehicle.
        """
        vehicles = [
            Vehicle(capacity=instance.capacity) for _ in range(instance.vehicle_count)
        ]
        clients_by_demand = sorted(
            instance.clients.values(), key=lambda c: (-c.demand, c.id)
        )
        for client in clients_by_demand:
            vehicle = FirstFitSolutionGenerator._first_vehicle_with_capacity(
                vehicles, client.demand
            )
            if vehicle is None:
                return None

            vehicle.insert_client(len(vehicle.route), client)

        return Solution(vehicles=vehicles)

    @staticmethod
    def _first_vehicle_with_capacity(
        vehicles: list[Vehicle], demand: int
    ) -> Vehicle | None:
        for vehicle in vehicles:
            remaining_capacity = vehicle.capacity - vehicle.route.total_demand
            if demand <= remaining_capacity:
                return vehicle
        return None
