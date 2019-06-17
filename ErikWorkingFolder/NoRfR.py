import os
try:
	os.chdir(os.path.join(os.getcwd(), 'final assignment'))
	print(os.getcwd())
except:
	pass

import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ema_workbench import (Constraint,Scenario,Model, CategoricalParameter, save_results,MultiprocessingEvaluator, ema_logging, SequentialEvaluator,
                           ScalarOutcome, TimeSeriesOutcome, IntegerParameter, RealParameter, Policy)

from ema_workbench.analysis import parcoords
from ema_workbench.em_framework.optimization import (HyperVolume, EpsilonProgress)
from dike_model_function_V2_0 import (DikeNetwork,DikeNetworkTS)  # @UnresolvedImport
from Gelderlandproposal import get_model_for_problem_formulation

                                        

from ema_workbench.analysis import pairs_plotting

print(__name__)


if __name__ == '__main__':
    
    ema_logging.log_to_stderr(ema_logging.INFO)

    #generate the model --Change the argument for different actor formulations
    model, planning_steps = get_model_for_problem_formulation(1, outcome_type='scalar', direction = ScalarOutcome.MINIMIZE)
    #MAXIMIZE outcomes for worst case optimization....def

    #create reference case of policy levers all set to 0...'do nothing'
    #levs = []
    #for lev in model.levers:
    #    levs.append(lev)
    #reference_scenario = Scenario("reference", **{lever.name:0 for lever in levs})

 

    n_scenarios = 100
    n_policies = 10
    
    with MultiprocessingEvaluator(model, n_processes=10) as evaluator:
        results = evaluator.perform_experiments(scenarios=n_scenarios, policies=n_policies,
                                                reporting_frequency=50)
    #save results !!
    save_results(results, 'noRfR_Geld.tar.gz')
    
    fig, axes = pairs_plotting.pairs_scatter(experiments=experiments, outcomes=outcomes, group_by='policy',
                                         legend=False)
    fig.set_size_inches(16,12)
    plt.show()




    