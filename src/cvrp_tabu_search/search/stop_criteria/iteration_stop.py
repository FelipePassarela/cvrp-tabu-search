from pydantic import NonNegativeInt
from pydantic.dataclasses import dataclass as validated_dataclass

from ..search_progress import SearchProgress
from .stop_criterion import StopCriterion


@validated_dataclass(frozen=True)
class IterationStop(StopCriterion):
    max_iterations: NonNegativeInt

    def should_stop(self, progress: SearchProgress) -> bool:
        return progress.completed_iterations >= self.max_iterations
