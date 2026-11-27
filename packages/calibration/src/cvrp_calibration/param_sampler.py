from typing import Protocol

from cvrp_core.search.tabu import TabuSearchConfig


class ParamSampler(Protocol):
    """Provide a tabu search configuration for calibration."""

    def sample(self) -> TabuSearchConfig: ...
