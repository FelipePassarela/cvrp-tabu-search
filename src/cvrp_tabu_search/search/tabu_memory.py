from collections.abc import Hashable, Iterable
from typing import Annotated

from pydantic import NonNegativeInt, SkipValidation, validate_call


class TabuMemory[Key: Hashable]:
    """Track temporary key blocks by search iteration."""

    def __init__(self) -> None:
        self._blocked_through_by_key: dict[Key, int] = {}

    @validate_call
    def register(
        self,
        keys: Annotated[Iterable[Key], SkipValidation],
        *,
        iteration: NonNegativeInt,
        tenure: NonNegativeInt,
    ) -> None:
        """Block keys from an applied move through iteration + tenure, inclusive."""
        if tenure == 0:
            return

        blocked_through = iteration + tenure
        for key in keys:
            self._blocked_through_by_key[key] = blocked_through

    @validate_call
    def is_tabu(
        self,
        keys: Annotated[Iterable[Key], SkipValidation],
        *,
        iteration: NonNegativeInt,
    ) -> bool:
        """Report whether any of the given keys is blocked this iteration."""
        for key in keys:
            blocked_through = self._blocked_through_by_key.get(key)
            if blocked_through is not None and iteration <= blocked_through:
                return True
        return False

    @validate_call
    def discard_expired(self, *, iteration: NonNegativeInt) -> None:
        """Remove entries whose last blocked iteration has already passed."""
        expired_keys = [
            key
            for key, blocked_through in self._blocked_through_by_key.items()
            if blocked_through < iteration
        ]
        for key in expired_keys:
            del self._blocked_through_by_key[key]
