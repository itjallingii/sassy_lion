import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys

from ema_workbench import (Model, CategoricalParameter, ScalarOutcome, 
                           TimeSeriesOutcome, IntegerParameter, RealParameter,
                           MultiprocessingEvaluator, ema_logging,
                           perform_experiments, SequentialEvaluator)

from ema_workbench.util.utilities import load_results

from ema_workbench.analysis import prim

def load_tar(dike_names):
	results = {}
	for name in dike_names:
		results[name] = load_results('{}_results_1.tar.gz'.format(name)) # CHANGE FROM 'results_1' TO 'results' DEPENDING ON CASE 

	return results

def get_exp_and_outcomes(results):
	experiments = {}
	outcomes = {}
	for key in results.keys():
		experiments[key] = results[key][0]
		outcomes[key] = results[key][1]

		# print(outcomes['A.1'])

	return experiments, outcomes

def do_PRIM(experiments, outcomes, outcome_name='Expected Annual Damage', key='A.1', thresh=0.5, alpha=0.05, perc=90):
	uncert = {}
	levers = {}
	data = {}
	y = {}
	prim_alg_uncert = {}
	prim_alg_levers = {}
	box_uncert = {}
	box_levers = {}

	uncert[key] = experiments[key].iloc[:,:19]
	levers[key] = experiments[key].iloc[:,20:-3]
	data[key] = outcomes[key][outcome_name+' '+key.replace('.','')]

	#### CHANGE BACK TO 90 FOR A2-5 (OR 99.5 FOR A1) 
	y[key] = data[key] > np.percentile(data[key], perc) 

	# prim_alg_uncert[key] = prim.Prim(uncert[key], y[key], threshold=thresh, peel_alpha=alpha, obj_function=prim.PRIMObjectiveFunctions.LENIENT2)
	prim_alg_uncert[key] = prim.Prim(uncert[key], y[key], threshold=thresh, peel_alpha=alpha)
	prim_alg_levers[key] = prim.Prim(levers[key], y[key], threshold=thresh, peel_alpha=alpha)

	box_uncert[key] = prim_alg_uncert[key].find_box()
	box_levers[key] = prim_alg_levers[key].find_box()

	return box_uncert, box_levers

if __name__ == '__main__':
	dike_names = ['A.1','A.2','A.3','A.4','A.5']
	results = load_tar(dike_names)
	experiments, outcomes = get_exp_and_outcomes(results)
	# outcome_name is 'Expected Annual Damage' (default), 'Expected Number of Deaths in', or 'Investment Costs'
	do_PRIM(experiments, outcomes)
	