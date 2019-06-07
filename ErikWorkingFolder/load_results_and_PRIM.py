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

def load_tar(dike_names):
	results = {}
	for name in dike_names:
		results[name] = load_results('{}_results.tar.gz'.format(name))

	return results

if __name__ == '__main__':
	dike_names = ['A.1','A.2']
	# dike_names = ['A.1','A.2','A.3','A.4','A.5']
	results = load_tar(dike_names)
	print(results)