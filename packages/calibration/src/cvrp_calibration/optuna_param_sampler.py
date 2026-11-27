from optuna.distributions import IntDistribution
from optuna.trial import FrozenTrial, Trial
from pydantic import ConfigDict
from pydantic.dataclasses import dataclass as validated_dataclass

from cvrp_core.search.stop_criteria import IterationStop, StagnationStop
from cvrp_core.search.tabu import TabuSearchConfig, TabuTenure

from .param_sampler import ParamSampler


@validated_dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class OptunaParamSampler(ParamSampler):
    """Sample the tabu search parameters for an Optuna trial."""

    trial: Trial | FrozenTrial
    max_iterations: IntDistribution
    stagnation_limit: IntDistribution
    tabu_tenure_min: IntDistribution
    tabu_tenure_max: IntDistribution

    def __post_init__(self) -> None:
        if self.max_iterations.low < 0:
            raise ValueError("max_iterations must allow only non-negative values.")
        if self.stagnation_limit.low < 1:
            raise ValueError("stagnation_limit must allow only positive values.")
        if self.tabu_tenure_min.low < 0 or self.tabu_tenure_max.low < 0:
            raise ValueError("Tabu tenure distributions must be non-negative.")
        if self.tabu_tenure_min.high > self.tabu_tenure_max.high:
            raise ValueError("Every tabu tenure minimum must have a feasible maximum.")

    def sample(self) -> TabuSearchConfig:
        """Suggest parameters for a trial or recover them from a completed trial."""
        max_iterations = self._suggest_int("max_iterations", self.max_iterations)
        stagnation_limit = self._suggest_int("stagnation_limit", self.stagnation_limit)
        iteration_stop = IterationStop(max_iterations=max_iterations)
        stagnation_stop = StagnationStop(stagnation_limit=stagnation_limit)
        return TabuSearchConfig(
            iteration_stop=iteration_stop,
            tenure=self._sample_tenure(),
            stop_criteria=(stagnation_stop,),
        )

    def _sample_tenure(self) -> TabuTenure:
        minimum = self._suggest_int("tabu_tenure_min", self.tabu_tenure_min)
        maximum = self._suggest_int(
            "tabu_tenure_max", self.tabu_tenure_max, lower_bound=minimum
        )
        return TabuTenure(minimum=minimum, maximum=maximum)

    def _suggest_int(
        self,
        name: str,
        distribution: IntDistribution,
        *,
        lower_bound: int | None = None,
    ) -> int:
        low = distribution.low
        if lower_bound is not None and lower_bound > low:
            # Advance to the first value on the original grid at or above the bound.
            offset = lower_bound - low
            steps = (offset + distribution.step - 1) // distribution.step
            low += steps * distribution.step

        return self.trial.suggest_int(
            name, low, distribution.high, step=distribution.step, log=distribution.log
        )
