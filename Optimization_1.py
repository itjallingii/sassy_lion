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
from problem_formulation_V2_1 import get_model_for_actor_problem_formulation

                                        


print(__name__)


if __name__ == '__main__':
    
    ema_logging.log_to_stderr(ema_logging.INFO)

    #generate the model --Change the argument for different actor formulations
    model, planning_steps = get_model_for_actor_problem_formulation(1, outcome_type='scalar', direction = ScalarOutcome.MINIMIZE)
    #MAXIMIZE outcomes for worst case optimization....def

    #create reference case of policy levers all set to 0...'do nothing'
    #levs = []
    #for lev in model.levers:
    #    levs.append(lev)
    #reference_scenario = Scenario("reference", **{lever.name:0 for lever in levs})

    uncs = []
    for unc in model.uncertainties:
       uncs.append(unc)
    reference_scenario = Scenario('reference', **{'A.1_pfail' : 0.5, 'A.2_pfail' :0.5,'A.3_pfail' : 0.5,'A.4_pfail' : 0.5,'A.5_pfail' : 0.5,
    'A.1_Bmax' : 175,'A.2_Bmax' : 175,'A.3_Bmax' : 175,'A.4_Bmax' : 175,'A.5_Bmax' : 175,
    'A.1_Brate' : 3,'A.2_Brate' : 3,'A.3_Brate' : 3,'A.4_Brate': 3,'A.5_Brate' : 3, 'discount rate' :6, 'A.0_ID flood wave shape' : 150})

    constraints = [Constraint("Expected Number of Deaths in Gelderland", outcome_names="Expected Number of Deaths in Gelderland",
                          function=lambda x:max(0, x-1)), 
                          Constraint("Expected Number of Deaths in Overijssel", outcome_names="Expected Number of Deaths in Overijssel",
                          function=lambda x:max(0, x-1)) ]

    #define convergence metrics --COMPUTATIONALLY EXPENSIVE SO COMMENT OUT WHERE NECESSARY
    #specifying min and max values...play around with this max!!
    convergence_metrics = [HyperVolume(minimum=[0,0,0,0,0,0,0,0], maximum=[2e08,100,10,2e08,100,10,2e08,100]), EpsilonProgress()]

    #with both searchover = 'uncertainties' then = 'levers'...but then change the refernece!!
    with MultiprocessingEvaluator(model) as evaluator:
        results, convergence1 = evaluator.optimize(nfe=15000, searchover='levers', logging_freq = 1,
                                epsilons=[1000,100,0.1, 1000,100,0.1,1000,100], convergence = convergence_metrics,reference=reference_scenario)
 
    #save results !!
    #save_results(results, 'MORDM_evaluation_0.tar.gz') #change names to not overwrite each time
    #policies = policies.drop([o.name for o in model.outcomes], axis=1)
    #policies.to_csv('mordm polices_0.csv')
    results.to_csv('MORDM_evaluation_1.csv')

    #plot tradeoffs
    data = results.loc[:, [o.name for o in model.outcomes]]
    limits = parcoords.get_limits(data)
    limits.loc[0,[o.name for o in model.outcomes]] = 0

    paraxes = parcoords.ParallelAxes(limits)
    paraxes.plot(data)
    plt.show(block=True)

    #can also plot convergence here...
    fig, (ax1, ax2) = plt.subplots(ncols=2, sharex=True, figsize=(8,4))
    ax1.plot(convergence1.nfe, convergence1.epsilon_progress)
    ax1.set_ylabel('$\epsilon$-progress')
    ax2.plot(convergence1.nfe, convergence1.hypervolume)
    ax2.set_ylabel('hypervolume')


    ax1.set_xlabel('number of function evaluations')
    ax2.set_xlabel('number of function evaluations')
    plt.show(block=True)

    print('convergence is',convergence1.nfe)
    print('convergence is',convergence1.epsilon_progress)

    

