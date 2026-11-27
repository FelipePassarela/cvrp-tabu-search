from dataclasses import replace

import optuna
import pytest
from optuna.distributions import IntDistribution
from pydantic import ValidationError

from cvrp_calibration.optuna_param_sampler import OptunaParamSampler
from cvrp_core.search.stop_criteria import IterationStop, StagnationStop
from cvrp_core.search.tabu import TabuSearchConfig, TabuTenure


@pytest.mark.parametrize(
    ("tenure_minimum", "first_allowed_maximum"), [(2, 3), (6, 7), (9, 9)]
)
def test_sample_preserves_the_grid_of_feasible_tabu_maxima(
    tenure_minimum: int, first_allowed_maximum: int
) -> None:
    study = optuna.create_study()
    study.enqueue_trial({"tabu_tenure_min": tenure_minimum})
    trial = study.ask()
    sampler = OptunaParamSampler(
        trial=trial,
        max_iterations=IntDistribution(20, 100, log=True),
        stagnation_limit=IntDistribution(10, 10),
        tabu_tenure_min=IntDistribution(2, 9),
        tabu_tenure_max=IntDistribution(3, 9, step=2),
    )

    config = sampler.sample()
    study.tell(trial, 0.0)

    assert trial.distributions["max_iterations"] == sampler.max_iterations
    assert trial.distributions["tabu_tenure_max"] == IntDistribution(
        first_allowed_maximum, 9, step=2
    )
    tenure = config.tenure
    assert tenure.minimum == tenure_minimum
    assert tenure.maximum in range(first_allowed_maximum, 10, 2)
    completed_sampler = replace(sampler, trial=study.best_trial)
    assert completed_sampler.sample() == config


def test_sample_fixed_values_configures_search_with_tabu_disabled() -> None:
    study = optuna.create_study()
    trial = study.ask()
    sampler = OptunaParamSampler(
        trial=trial,
        max_iterations=IntDistribution(0, 0),
        stagnation_limit=IntDistribution(10, 10),
        tabu_tenure_min=IntDistribution(0, 0),
        tabu_tenure_max=IntDistribution(0, 0),
    )

    config = sampler.sample()
    study.tell(trial, 0.0)

    assert config == TabuSearchConfig(
        iteration_stop=IterationStop(max_iterations=0),
        tenure=TabuTenure(0, 0),
        stop_criteria=(StagnationStop(stagnation_limit=10),),
    )


@pytest.mark.parametrize(
    ("field", "low", "high", "message"),
    [
        ("max_iterations", -1, 20, "max_iterations must allow only non-negative"),
        ("stagnation_limit", 0, 20, "stagnation_limit must allow only positive"),
        ("tabu_tenure_min", -1, 10, "Tabu tenure distributions must be non-negative"),
        ("tabu_tenure_max", -1, 10, "Tabu tenure distributions must be non-negative"),
        ("tabu_tenure_min", 1, 11, "Every tabu tenure minimum must have a feasible"),
    ],
)
def test_invalid_distributions_are_rejected_before_sampling(
    field: str, low: int, high: int, message: str
) -> None:
    sampler = OptunaParamSampler(
        trial=optuna.create_study().ask(),
        max_iterations=IntDistribution(20, 100),
        stagnation_limit=IntDistribution(5, 20),
        tabu_tenure_min=IntDistribution(1, 5),
        tabu_tenure_max=IntDistribution(3, 10),
    )

    with pytest.raises(ValidationError, match=message):
        replace(sampler, **{field: IntDistribution(low, high)})
