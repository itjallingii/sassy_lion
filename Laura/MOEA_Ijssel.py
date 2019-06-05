from ema_workbench import (Model, RealParameter, ScalarOutcome,
                           MultiprocessingEvaluator, ema_logging,
                           Constant,perform_experiments, SequentialEvaluator)

ema_logging.log_to_stderr(ema_logging.INFO)

from dike_model_function import DikeNetwork 
from problem_formulation import get_model_for_problem_formulation

model, planning_steps = get_model_for_problem_formulation(1)

with SequentialEvaluator(model) as evaluator:
    experiments, outcomes = evaluator.perform_experiments(scenarios=2, policies=2)