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
		results[name] = load_results('{}_results.tar.gz'.format(name))

	return results

def get_exp_and_outcomes(results):
	experiments = {}
	outcomes = {}
	for key in results.keys():
		experiments[key] = results[key][0]
		outcomes[key] = results[key][1]

	return experiments, outcomes

def do_PRIM(experiments, outcomes, outcome_name='Expected Annual Damage'):
	uncert = {}
	levers = {}
	data = {}
	prim_alg_uncert = {}
	prim_alg_levers = {}
	box_uncert = {}
	box_levers = {}

	for key in experiments.keys():
		uncert[key] = experiments[key].drop(experiments[key].columns[16:-2], axis=1)
		levers[key] = experiments[key].iloc[:,16:-1]
		data[key] = outcomes['A.1'][outcome_name+' '+key.replace('.','')]

		prim_alg_uncert[key] = prim.Prim(uncert[key], data[key], threshold=0.6)
		prim_alg_levers[key] = prim.Prim(levers[key], data[key], threshold=0.6)

		box_uncert[key] = prim_alg_uncert.find_box()
		box_levers[key] = prim_alg_levers.find_box()

	return

if __name__ == '__main__':
	dike_names = ['A.1','A.2','A.3','A.4','A.5']
	results = load_tar(dike_names)
	experiments, outcomes = get_exp_and_outcomes(results)
	print(outcomes['A.1'])
	# outcome_name is 'Expected Annual Damage' (default), 'Expected Number of Deaths in', or 'Investment Costs'
	do_PRIM(experiments, outcomes)
	