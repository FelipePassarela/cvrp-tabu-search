import pytest
from pydantic import ValidationError

from cvrp_core.search.search_progress import SearchProgress
from cvrp_core.search.stop_criteria import IterationStop


def test_iteration_stop_triggers_at_the_limit_even_when_cost_improves() -> None:
    progress = SearchProgress(initial_cost=100)
    criterion = IterationStop(max_iterations=2)

    progress.record_iteration(solution_cost=90)
    assert not criterion.should_stop(progress)

    progress.record_iteration(solution_cost=80)
    assert criterion.should_stop(progress)

    progress.record_iteration(solution_cost=70)
    assert criterion.should_stop(progress)


def test_zero_iteration_limit_stops_at_the_initial_solution() -> None:
    progress = SearchProgress(initial_cost=100)

    assert IterationStop(max_iterations=0).should_stop(progress)


def test_iteration_stop_rejects_a_negative_limit() -> None:
    with pytest.raises(ValidationError, match="max_iterations"):
        IterationStop(max_iterations=-1)
