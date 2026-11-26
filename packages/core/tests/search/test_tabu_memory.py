import pytest
from pydantic import ValidationError

from cvrp_core.search.tabu_memory import TabuMemory


def test_tenure_covers_the_next_iterations_inclusively() -> None:
    memory = TabuMemory[str]()
    key = "first"
    applied_iteration = 5
    tenure = 2

    memory.register((key,), iteration=applied_iteration, tenure=tenure)

    assert memory.is_tabu((key,), iteration=6)
    assert memory.is_tabu((key,), iteration=7)
    assert not memory.is_tabu((key,), iteration=8)


def test_registering_a_key_again_uses_the_new_tenure() -> None:
    memory = TabuMemory[str]()
    key = "first"
    memory.register((key,), iteration=1, tenure=6)

    memory.register((key,), iteration=2, tenure=2)

    assert memory.is_tabu((key,), iteration=4)
    assert not memory.is_tabu((key,), iteration=5)


def test_discard_expired_keeps_the_key_that_expires_this_iteration() -> None:
    memory = TabuMemory[str]()
    expired_key = "first"
    active_key = "second"
    memory.register((expired_key,), iteration=1, tenure=2)
    memory.register((active_key,), iteration=2, tenure=2)

    memory.discard_expired(iteration=4)

    assert expired_key not in memory._blocked_through_by_key
    assert memory.is_tabu((active_key,), iteration=4)


def test_zero_tenure_does_not_register_a_block() -> None:
    memory = TabuMemory[str]()
    key = "first"

    memory.register((key,), iteration=1, tenure=0)

    assert not memory.is_tabu((key,), iteration=1)


@pytest.mark.parametrize(
    "iteration,tenure,invalid_argument",
    [(-1, 1, "iteration"), (1, -1, "tenure")],
    ids=["iteration", "tenure"],
)
def test_register_rejects_negative_arguments(
    iteration: int, tenure: int, invalid_argument: str
) -> None:
    memory = TabuMemory[str]()
    key = "first"

    with pytest.raises(ValidationError) as error:
        memory.register((key,), iteration=iteration, tenure=tenure)

    detail = error.value.errors()[0]
    assert detail["loc"] == (invalid_argument,)
    assert detail["type"] == "greater_than_equal"


def test_is_tabu_rejects_a_negative_iteration() -> None:
    memory = TabuMemory[str]()
    key = "first"

    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        memory.is_tabu((key,), iteration=-1)


def test_discard_expired_rejects_a_negative_iteration() -> None:
    memory = TabuMemory[str]()

    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        memory.discard_expired(iteration=-1)
