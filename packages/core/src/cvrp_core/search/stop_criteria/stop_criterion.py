from abc import ABC, abstractmethod

from ..search_progress import SearchProgress


class StopCriterion(ABC):
    @abstractmethod
    def should_stop(self, progress: SearchProgress) -> bool:
        """Return whether the search should end before the next iteration."""
