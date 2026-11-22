from typing import Literal, NamedTuple

from ..routes import Route

type TabuKeyTuple = tuple[Literal["reverse", "return"], int, int]


class ReversalTabuKey(NamedTuple):
    kind: Literal["reverse"]
    lower_customer: int
    upper_customer: int


class ReturnTabuKey(NamedTuple):
    kind: Literal["return"]
    customer: int
    vehicle_index: int


type TabuKey = ReversalTabuKey | ReturnTabuKey


class RouteUpdate(NamedTuple):
    vehicle_index: int
    route: Route
    load: int


class Move(NamedTuple):
    route_updates: tuple[RouteUpdate, ...]
    cost: int
    tabu_keys: tuple[TabuKey, ...]
    customers: tuple[int, ...]

    @classmethod
    def from_candidate(
        cls,
        route_updates: tuple[tuple[int, Route, int], ...],
        cost: int,
        tabu_keys: tuple[TabuKeyTuple, ...],
        customers: tuple[int, ...],
    ) -> "Move":
        return cls(
            route_updates=tuple(RouteUpdate(*update) for update in route_updates),
            cost=cost,
            tabu_keys=tuple(_named_tabu_key(key) for key in tabu_keys),
            customers=customers,
        )


def _named_tabu_key(key: TabuKeyTuple) -> TabuKey:
    kind, first, second = key
    if kind == "reverse":
        return ReversalTabuKey(kind, first, second)

    return ReturnTabuKey(kind, first, second)
