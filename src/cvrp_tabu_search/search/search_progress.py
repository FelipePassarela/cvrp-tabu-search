class SearchProgress:
    """Track completed iterations and strict improvements over the best cost."""

    def __init__(self, initial_cost: int) -> None:
        self._best_cost = initial_cost
        self._completed_iterations = 0
        self._iterations_without_improvement = 0

    @property
    def best_cost(self) -> int:
        return self._best_cost

    @property
    def completed_iterations(self) -> int:
        return self._completed_iterations

    @property
    def iterations_without_improvement(self) -> int:
        return self._iterations_without_improvement

    def record_iteration(self, solution_cost: int) -> bool:
        """Record a completed iteration and report whether it improved the best cost."""
        is_new_best = solution_cost < self._best_cost
        self._completed_iterations += 1
        if is_new_best:
            self._best_cost = solution_cost
            self._iterations_without_improvement = 0
        else:
            self._iterations_without_improvement += 1
        return is_new_best
