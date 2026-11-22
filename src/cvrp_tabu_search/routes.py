from collections.abc import Iterable, Sequence

type Route = list[int]
type Coordinates = Sequence[Sequence[float]]


class Vehicle:
    def __init__(self, capacity: int) -> None:
        self.capacity = capacity
        self.load = 0
        self.route: Route = []

    def add_customer(self, customer: int, demand: int) -> bool:
        new_load = self.load + demand
        if new_load > self.capacity:
            return False

        self.load = new_load
        self.route.append(customer)
        return True


def distance(first: int, second: int, coordinates: Coordinates) -> int:
    # Customer IDs in the instance file are one-based.
    first_x, first_y = coordinates[first - 1]
    second_x, second_y = coordinates[second - 1]
    delta_x = second_x - first_x
    delta_y = second_y - first_y
    euclidean_distance = (delta_x**2 + delta_y**2) ** 0.5
    return int(euclidean_distance + 0.5)


def route_cost(route: Route, coordinates: Coordinates, depot: int) -> int:
    cost = 0
    previous = depot

    for customer in route:
        cost += distance(previous, customer, coordinates)
        previous = customer

    return cost + distance(previous, depot, coordinates)


def build_initial_solution(
    vehicle_count: int,
    dimension: int,
    capacity: int,
    demands: Sequence[int],
    depot: int,
) -> list[Vehicle] | None:
    fleet = [Vehicle(capacity) for _ in range(vehicle_count)]

    def customer_demand(customer: int) -> int:
        return demands[customer - 1]

    customers = sorted(
        (customer for customer in range(1, dimension + 1) if customer != depot),
        key=customer_demand,
        reverse=True,
    )

    for customer in customers:
        demand = customer_demand(customer)
        for vehicle in fleet:
            if vehicle.add_customer(customer, demand):
                break
        else:
            return None

    return fleet


def copy_routes(fleet: Iterable[Vehicle]) -> list[Route]:
    return [vehicle.route.copy() for vehicle in fleet]


def reverse_segment(route: Route, start: int, end: int) -> Route:
    updated_route = route.copy()
    segment = updated_route[start : end + 1]
    segment.reverse()
    updated_route[start : end + 1] = segment
    return updated_route
