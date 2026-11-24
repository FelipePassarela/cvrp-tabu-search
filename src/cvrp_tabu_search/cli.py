from argparse import ArgumentParser
from pathlib import Path

from cvrp_tabu_search.instance_factory import load_instance

_DEFAULT_PATH = Path(__file__).with_name("data") / "A-n32-k5.vrp"


def app() -> None:
    parser = ArgumentParser(description="Load a CVRP instance from a .vrp file.")
    parser.add_argument("path", nargs="?", type=Path, default=_DEFAULT_PATH)
    arguments = parser.parse_args()

    try:
        instance = load_instance(arguments.path)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    print(instance)


if __name__ == "__main__":
    app()
