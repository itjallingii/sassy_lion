import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ema_workbench import (Model, CategoricalParameter,
                           ScalarOutcome, TimeSeriesOutcome, IntegerParameter, RealParameter)

from ema_workbench import (MultiprocessingEvaluator, ema_logging,
                           perform_experiments, SequentialEvaluator)

from dike_model_function_V2_0 import (DikeNetwork,DikeNetworkTS)  # @UnresolvedImport
from problem_formulation_V2_2 import get_model_for_actor_problem_formulation

from ema_workbench.util.utilities import save_results

# Problem formulations:
#    get_model_for_actor_problem_formulation(problem_formulation_id, outcome_type='time_series')
#    problem_formulation_id options
#        1 - RWS (GOOD)
#        2 - Environmental interest group
#        3 - Transport company 
#        4 - Delta commission
#        5 - Gelderland (GOOD)
#        6 - Overijssel (GOOD)s
#        7 - Dike rings 1 and 2
#        8 - Dike ring 1
#        9 - Dike ring 2
#        10 - Dike ring 3
#        11 - Dike ring 4
#        12 - Dike ring 5
#
#    outcome_type options
#        'time_series' (default)
#        'scalar'

def make_models(dike_nums):
	models = {}
	for num in dike_nums:
		models['A.{}'.format(num)] = get_model_for_actor_problem_formulation(
			num+7, outcome_type='scalar')
	return models

def run_models(model_dict, num_scenarios=1, num_policies=1):
	results = {}
	for key in model_dict.keys():
		with MultiprocessingEvaluator(model_dict[key][0]) as evaluator:
			results[key] = evaluator.perform_experiments(
	        	scenarios=num_scenarios, policies=num_policies, reporting_frequency=50)
	return results

def get_experiments_and_outcomes(results):
	experiments = {}
	outcomes = {}
	for key in results.keys():
		experiments[key] = results[key][0]
		outcomes[key] = results[key][1]

	return experiments, outcomes

def save_results_as_tar(results):
	for key in results.keys():
		save_results(results[key], '{}_results.tar.gz'.format(key))

if __name__ == '__main__':
	dike_nums = [1,2,3,4,5]
	n_scenarios = 100
	n_policies = 100
	models = make_models(dike_nums)
	results = run_models(models,num_scenarios=n_scenarios,num_policies=n_policies)
	experiments, outcomes = get_experiments_and_outcomes(results)
	save_results_as_tar(results)
