from collections.abc import Mapping

from ..routes import Route
from .moves import Move, TabuKeyTuple
from .shared import is_tabu


class MoveSelector:
    def __init__(
        self,
        tabu_list: Mapping[TabuKeyTuple, int],
        iteration: int,
        best_cost: int,
        frequencies: Mapping[int, int],
        *,
        diversify: bool,
    ) -> None:
        self._tabu_list = tabu_list
        self._iteration = iteration
        self._best_cost = best_cost
        self._frequencies = frequencies
        self._diversify = diversify
        self._best_priority: tuple[int, ...] | None = None
        self.best_move: Move | None = None

    def consider(
        self,
        route_updates: tuple[tuple[int, Route, int], ...],
        cost: int,
        test_keys: tuple[TabuKeyTuple, ...],
        tabu_keys: tuple[TabuKeyTuple, ...],
        customers: tuple[int, ...],
    ) -> None:
        for key in test_keys:
            if is_tabu(self._tabu_list, key, self._iteration, cost, self._best_cost):
                return

        priority: tuple[int, ...] = (cost,)
        if self._diversify:
            move_frequency = sum(
                self._frequencies.get(customer, 0) for customer in customers
            )
            priority = (move_frequency, cost)

        if self._best_priority is None or priority < self._best_priority:
            self._best_priority = priority
            # Build named records only when a candidate becomes the best move.
            self.best_move = Move.from_candidate(
                route_updates, cost, tabu_keys, customers
            )
