from pydantic import ConfigDict
from pydantic.dataclasses import dataclass as validated_dataclass

from ..stop_criteria import IterationStop, StopCriterion
from .tenure import DEFAULT_TABU_TENURE, TabuTenure


@validated_dataclass(frozen=True, config=ConfigDict(arbitrary_types_allowed=True))
class TabuSearchConfig:
    """Configure tabu tenure and search stopping criteria."""

    iteration_stop: IterationStop
    tenure: TabuTenure = DEFAULT_TABU_TENURE
    stop_criteria: tuple[StopCriterion, ...] = ()
