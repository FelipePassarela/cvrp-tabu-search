from pathlib import Path
from typing import Annotated

import typer

DEFAULT_INSTANCE_PATH = Path(__file__).with_name("data") / "A-n32-k5.vrp"

InstancePath = Annotated[
    Path,
    typer.Argument(
        help="CVRP instance file.",
        dir_okay=False,
        exists=True,
        show_default=DEFAULT_INSTANCE_PATH.name,
    ),
]
IterationLimit = Annotated[
    int, typer.Option(min=0, help="Maximum number of iterations.")
]
StagnationLimit = Annotated[
    int,
    typer.Option(
        min=1, help="Maximum number of consecutive iterations without improvement."
    ),
]
TabuTenureMinimum = Annotated[
    int, typer.Option(min=0, help="Minimum tabu duration in iterations.")
]
TabuTenureMaximum = Annotated[
    int, typer.Option(min=0, help="Maximum tabu duration in iterations.")
]
RandomSeed = Annotated[
    int | None, typer.Option(help="Seed for reproducing tabu tenure draws.")
]
