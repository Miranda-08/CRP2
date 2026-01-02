import pathlib
from unified_planning.shortcuts import OneshotPlanner, get_environment
from unified_planning.engines.results import POSITIVE_OUTCOMES
from unified_planning.io import PDDLReader

def main():
    base_path = pathlib.Path(__file__).parent.resolve()
    get_environment().credits_stream = None

    reader = PDDLReader()
    domain_file = base_path / "domain.pddl"
    problem_file = base_path / "problem.pddl"

    problem = reader.parse_problem(domain_file, problem_file)

    with OneshotPlanner(problem_kind=problem.kind, name="pyperplan") as planner:
        result = planner.solve(problem)

    print("Status:", result.status)
    if result.status in POSITIVE_OUTCOMES and result.plan is not None:
        print("\nThe following plan was found:\n")
        for plan_action in result.plan.actions:
            print(f"{plan_action.action.name}{plan_action.actual_parameters}")
    else:
        print("No plan found.")

if __name__ == "__main__":
    main()