from argparse import ArgumentDefaultsHelpFormatter, ArgumentParser, Namespace
from pathlib import Path

from cvrp_tabu_search.search.instance_factory import load_instance
from cvrp_tabu_search.search.stop_criteria import IterationStop, StagnationStop
from cvrp_tabu_search.search.tabu_search import SearchResult, TabuSearch
from cvrp_tabu_search.search.tabu_tenure import DEFAULT_TABU_TENURE, TabuTenure

_DEFAULT_PATH = Path(__file__).with_name("data") / "A-n32-k5.vrp"


def app() -> None:
    parser = _build_parser()
    arguments = parser.parse_args()

    try:
        search = _build_search(arguments)
        instance = load_instance(arguments.path)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    result = search.solve(instance, seed=arguments.seed)
    if result is None:
        parser.exit(
            1, "First Fit Decreasing could not construct an initial solution.\n"
        )

    _print_result(result)


def _build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        description="Run tabu search on a CVRP instance.",
        formatter_class=ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path", nargs="?", type=Path, default=_DEFAULT_PATH, help="CVRP instance file."
    )
    parser.add_argument(
        "--max-iterations", type=int, default=60, help="Maximum number of iterations."
    )
    parser.add_argument(
        "--stagnation-limit",
        type=int,
        default=30,
        help="Maximum number of consecutive iterations without improvement.",
    )
    parser.add_argument(
        "--tabu-tenure-min",
        type=int,
        default=DEFAULT_TABU_TENURE.minimum,
        help="Minimum tabu duration in iterations.",
    )
    parser.add_argument(
        "--tabu-tenure-max",
        type=int,
        default=DEFAULT_TABU_TENURE.maximum,
        help="Maximum tabu duration in iterations.",
    )
    parser.add_argument(
        "--seed", type=int, help="Seed for reproducing tabu tenure draws."
    )
    return parser


def _build_search(arguments: Namespace) -> TabuSearch:
    iteration_stop = IterationStop(max_iterations=arguments.max_iterations)
    stagnation_stop = StagnationStop(stagnation_limit=arguments.stagnation_limit)
    tenure = TabuTenure(
        minimum=arguments.tabu_tenure_min, maximum=arguments.tabu_tenure_max
    )
    return TabuSearch(
        iteration_stop=iteration_stop, tenure=tenure, stop_criteria=(stagnation_stop,)
    )


def _print_result(result: SearchResult) -> None:
    print(f"Best cost: {result.best_cost}")
    print(f"Completed iterations: {result.completed_iterations}")
    for vehicle_number, route in enumerate(result.best_solution.routes, start=1):
        if route:
            client_ids = " ".join(str(client.id) for client in route)
            print(f"Route #{vehicle_number}: {client_ids}")


if __name__ == "__main__":
    app()
