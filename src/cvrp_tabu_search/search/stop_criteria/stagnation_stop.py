from pydantic import PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..search_progress import SearchProgress
from .stop_criterion import StopCriterion


@validated_dataclass(frozen=True)
class StagnationStop(StopCriterion):
    stagnation_limit: PositiveInt

    def should_stop(self, progress: SearchProgress) -> bool:
        return progress.iterations_without_improvement >= self.stagnation_limit
