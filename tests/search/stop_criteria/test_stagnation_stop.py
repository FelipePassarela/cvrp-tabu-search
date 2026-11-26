import pytest
from pydantic import ValidationError

from cvrp_tabu_search.search.search_progress import SearchProgress
from cvrp_tabu_search.search.stop_criteria import StagnationStop


def test_stagnation_counts_ties_and_improvements_that_do_not_beat_the_best() -> None:
    progress = SearchProgress(initial_cost=100)
    criterion = StagnationStop(stagnation_limit=3)
    assert not criterion.should_stop(progress)

    progress.record_iteration(solution_cost=110)
    progress.record_iteration(solution_cost=105)
    assert not criterion.should_stop(progress)

    progress.record_iteration(solution_cost=100)
    assert criterion.should_stop(progress)


def test_a_new_best_cost_restarts_the_stagnation_count() -> None:
    progress = SearchProgress(initial_cost=100)
    criterion = StagnationStop(stagnation_limit=2)
    progress.record_iteration(solution_cost=110)

    progress.record_iteration(solution_cost=90)
    progress.record_iteration(solution_cost=95)

    assert progress.best_cost == 90
    assert not criterion.should_stop(progress)

    progress.record_iteration(solution_cost=94)
    assert criterion.should_stop(progress)


def test_stagnation_stop_rejects_a_zero_limit() -> None:
    with pytest.raises(ValidationError, match="stagnation_limit"):
        StagnationStop(stagnation_limit=0)
