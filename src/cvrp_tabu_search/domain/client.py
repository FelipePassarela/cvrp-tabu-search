from pydantic import FiniteFloat, PositiveInt
from pydantic.dataclasses import dataclass as validated_dataclass


@validated_dataclass(frozen=True)
class Client:
    id: PositiveInt
    demand: PositiveInt
    coord_x: FiniteFloat
    coord_y: FiniteFloat
