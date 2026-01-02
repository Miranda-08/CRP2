import pathlib
from unified_planning.shortcuts import OneshotPlanner, get_environment
from unified_planning.engines.results import POSITIVE_OUTCOMES
from unified_planning.io import PDDLReader

base_path = pathlib.Path(__file__).parent.resolve()
get_environment().credits_stream = None

reader = PDDLReader()
domain_file = "domain-gripper.pddl"
problem_file = "problem-gripper.pddl"

problem = reader.parse_problem(base_path / domain_file,
                               base_path / problem_file)

with OneshotPlanner(problem_kind=problem.kind, name="pyperplan") as planner:
    result = planner.solve(problem)
    if result.status in POSITIVE_OUTCOMES:
        print("The following plan was found:\n")
        for i in range(len(result.plan.actions)):
            plan_action = result.plan.actions[i]
            print(f"{plan_action.action.name}{plan_action.actual_parameters}")
    else:
        print("No plan found.")
