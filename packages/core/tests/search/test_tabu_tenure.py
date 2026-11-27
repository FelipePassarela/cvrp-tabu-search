import pytest
from pydantic import ValidationError

from cvrp_core.search.tabu import TabuTenure


@pytest.mark.parametrize(
    ("minimum", "maximum"), [(-1, 3), (0, -1)], ids=["minimum", "maximum"]
)
def test_tabu_tenure_rejects_negative_bounds(minimum: int, maximum: int) -> None:
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        TabuTenure(minimum=minimum, maximum=maximum)


def test_tabu_tenure_rejects_a_minimum_above_the_maximum() -> None:
    with pytest.raises(ValidationError, match="Minimum tabu tenure"):
        TabuTenure(minimum=5, maximum=1)
