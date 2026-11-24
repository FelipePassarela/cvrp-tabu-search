from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class InversionTabuKey:
    lower_client_id: int
    upper_client_id: int


@dataclass(frozen=True, slots=True)
class ReturnTabuKey:
    client_id: int
    vehicle_index: int


type TabuKey = InversionTabuKey | ReturnTabuKey


@dataclass(frozen=True, slots=True)
class MoveTabuKeys:
    """Keys to check before applying a move and to register afterward."""

    to_check: tuple[TabuKey, ...]
    to_register: tuple[TabuKey, ...]
