from dataclasses import dataclass
from random import Random

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass as validated_dataclass

from ..domain import Depot
from .first_fit_solution_generator import FirstFitSolutionGenerator
from .instance import Instance
from .moves import Move, Neighbourhood
from .moves.tabu_keys import TabuKey
from .search_progress import SearchProgress
from .solution import Solution
from .solution_evaluator import SolutionEvaluator
from .stop_criteria import IterationStop, StopCriterion
from .tabu_memory import TabuMemory
from .tabu_tenure import TabuTenure


@dataclass(frozen=True)
class SearchResult:
    best_solution: Solution
    best_cost: int
    completed_iterations: int


@dataclass(frozen=True)
class _Candidate:
    solution: Solution
    cost: int
    keys_to_register: tuple[TabuKey, ...]


@validated_dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class TabuSearch:
    """Minimize CVRP cost with a fixed tenure or an inclusive sampling range."""

    iteration_stop: IterationStop
    tenure: TabuTenure = TabuTenure(minimum=1, maximum=15)
    stop_criteria: tuple[StopCriterion, ...] = ()

    def solve(
        self, instance: Instance, *, seed: int | None = None
    ) -> SearchResult | None:
        """Return the best solution, or None if First Fit cannot construct one.

        Pass a seed to reproduce the tenure draws for this run.
        """
        initial_solution = FirstFitSolutionGenerator.generate(instance)
        if initial_solution is None:
            return None

        return self._search(initial_solution, instance.depot, seed=seed)

    def _search(
        self, initial_solution: Solution, depot: Depot, *, seed: int | None
    ) -> SearchResult:
        initial_cost = SolutionEvaluator.evaluate(initial_solution, depot)
        progress = SearchProgress(initial_cost)
        tabu_memory = TabuMemory[TabuKey]()
        tenure_random = Random(seed)
        current_solution = initial_solution
        best_solution = initial_solution

        while not self._should_stop(progress):
            candidate = self._advance(
                current_solution, depot, progress, tabu_memory, tenure_random
            )
            if candidate is None:
                break

            current_solution = candidate.solution
            improved_best = progress.record_iteration(candidate.cost)
            if improved_best:
                best_solution = current_solution

        return SearchResult(
            best_solution=best_solution,
            best_cost=progress.best_cost,
            completed_iterations=progress.completed_iterations,
        )

    def _should_stop(self, progress: SearchProgress) -> bool:
        return self.iteration_stop.should_stop(progress) or any(
            criterion.should_stop(progress) for criterion in self.stop_criteria
        )

    def _advance(
        self,
        solution: Solution,
        depot: Depot,
        progress: SearchProgress,
        tabu_memory: TabuMemory[TabuKey],
        tenure_random: Random,
    ) -> _Candidate | None:
        iteration = progress.completed_iterations + 1
        tabu_memory.discard_expired(iteration=iteration)
        candidate = self._select_candidate(
            solution,
            depot,
            tabu_memory,
            iteration=iteration,
            best_cost=progress.best_cost,
        )
        if candidate is not None:
            tenure = self.tenure.draw(tenure_random)
            tabu_memory.register(
                candidate.keys_to_register, iteration=iteration, tenure=tenure
            )
        return candidate

    @staticmethod
    def _select_candidate(
        solution: Solution,
        depot: Depot,
        tabu_memory: TabuMemory[TabuKey],
        *,
        iteration: int,
        best_cost: int,
    ) -> _Candidate | None:
        best_candidate = None
        for move in Neighbourhood.generate_moves(solution):
            neighbor, cost = TabuSearch._evaluate_neighbor(solution, depot, move)
            if best_candidate is not None and cost >= best_candidate.cost:
                continue

            keys = move.tabu_keys(solution)
            improves_global_best = cost < best_cost
            if not improves_global_best and tabu_memory.is_tabu(
                keys.to_check, iteration=iteration
            ):
                continue

            best_candidate = _Candidate(neighbor, cost, keys.to_register)
        return best_candidate

    @staticmethod
    def _evaluate_neighbor(
        solution: Solution, depot: Depot, move: Move
    ) -> tuple[Solution, int]:
        neighbor = solution.copy()
        move.apply(neighbor)
        cost = SolutionEvaluator.evaluate(neighbor, depot)
        return neighbor, cost
