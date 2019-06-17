
import numpy as np
import scipy as sp
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from ema_workbench import (Constraint,Scenario,Model, CategoricalParameter, save_results,MultiprocessingEvaluator, ema_logging, SequentialEvaluator,
                           ScalarOutcome, TimeSeriesOutcome, IntegerParameter, RealParameter, Policy, save_results)

from ema_workbench.analysis import parcoords
from ema_workbench.em_framework.optimization import (HyperVolume, EpsilonProgress, GenerationalBorg)
from dike_model_function import (DikeNetwork)  # @UnresolvedImport
from problem_formulation_V2_2 import get_model_for_actor_problem_formulation

if __name__ == '__main__':
    
    ema_logging.log_to_stderr(ema_logging.INFO)

    #generate the model --Change the argument for different actor formulations
    #MAXIMIZE outcomes for worst case optimization....MINIMIZE for standard optimization
    #prob formulation 1 is agregated to 8 outcomes
    model, planning_steps = get_model_for_actor_problem_formulation(1, outcome_type='scalar', direction_optimize = ScalarOutcome.MINIMIZE)
    

    #create reference case of policy levers all set to 0...'do nothing'
    #reference_scenario = Scenario("reference", **{l.name:0 for l in model.levers})

    #create reference case of uncertainties (values as of documentation) 
    # Note that the 'insenstive uncertainties' are already constants from the problem_formulation
    
    #reference_scenario = Scenario("reference", 
    #                                **{'A.1_pfail' : 0.5, 'A.2_pfail' :0.5,'A.3_pfail' : 0.5,'A.4_pfail' : 0.5,'A.5_pfail' : 0.5,
    #                                'A.1_Bmax' : 175,'A.2_Bmax' : 175,'A.3_Bmax' : 175,'A.4_Bmax' : 175,
    #                                'discount rate 0' :1.5,'discount rate 1' :1.5,'discount rate 2' :1.5, 
    #                               'A.0_ID flood wave shape' : 4})
    #reference_scenario = Scenario("reference", **{u.name:0 for u in model.uncertainties}) #Nothing policy?
    # Build a user-defined scenario and policy:

    reference_values = {'Bmax': 175,  'pfail': 0.5,
                       'A.0_ID flood wave shape': 4}
    reference_values.update({'discount rate {}'.format(n): 1.5 for n in planning_steps})
    scen1 = {}

    for key in model.uncertainties:
        name_split = key.name.split('_')

    if len(name_split) == 1:
       scen1.update({key.name: reference_values[key.name]})
    else:
       scen1.update({key.name: reference_values[name_split[1]]})

    reference_scenario = Scenario('reference', **scen1)
    

    #'Individual risk' of dying from flood: 1/100,000 --> don't think there is a way of calculating in this model
    #population ratio of (Gelderland : Overijssel) equal to (2.048 mn : 1.148 mn) or (1.78 : 1) scales all 'expected deaths' and "expected costs"
    #constraints on equality within 10% 
    #constraints on max, as same as convergence metrics
    constraints = [Constraint('equal provinces deaths', outcome_names = ['Expected Number of Deaths in Overijssel',"Expected Number of Deaths in Gelderland"], 
                         function = lambda x,y: max(0,(abs(x*1.78-y))/(0.001+y)-0.1)),
                        Constraint('max provinces deaths', outcome_names = ['Expected Number of Deaths in Overijssel',"Expected Number of Deaths in Gelderland"], 
                         function = lambda x,y: max(0,x-1,y-1)),
                         Constraint('equal provinces damages', outcome_names = ['Expected Annual Damage Overijssel',"Expected Annual Damage Gelderland"], 
                        function = lambda x,y: max(0,(abs(x*1.78-y))/(0.0001+y)-0.1)),
                         Constraint('max provinces damages', outcome_names = ['Expected Annual Damage Overijssel',"Expected Annual Damage Gelderland"], 
                        function = lambda x,y: max(0,x-1e09,y-1e09)),
                         Constraint('max RWS costs', outcome_names = ['RfR Total Costs'], 
                        function = lambda x: max(0,x-1e09)),    
                        Constraint('max provinces investments', outcome_names = ['Dike Investment Costs Gelderland',"Dike Investment Costs Overijssel"], 
                         function = lambda x,y: max(0,x-1e09,y-1e09)),                        
                        ]

    #define convergence metrics 
    #specifying min and max values...play around with this max value!!
    convergence_metrics = [HyperVolume(minimum=[0,0,0,0,0,0,0], maximum=[5e09,5e09,5,5e09,5e09,5,5e09]), EpsilonProgress()]

    #all_results = []
    #Run searchover = 'uncertainties' and searchover = 'levers'...but then change the refernece case accordingly!!
    with MultiprocessingEvaluator(model) as evaluator:
        #for rep in range(5): ADD IN IN THE MORNING ( etc ) SEED
        
        results1, convergence1 = evaluator.optimize(
                                #algorithm =  GenerationalBorg,
                                nfe=12000, 
                                searchover='levers', 
                                reference = reference_scenario,
                                convergence = convergence_metrics,
                                constraints = constraints,
                                convergence_freq = 60,                                
                                logging_freq = 1,
                                epsilons=[10000,10000,0.00001, 10000,10000,0.00001,50000])

                                #algorithm=GenerationalBorg, #--> limited to real parameters only Is this the outcomes?

        #all_results.append(results1)
        #results1.to_csv('results_reference_MORDM_{}.csv', format(rep))
        #convergence1.to_csv('convergene_reference_MORDM_{}.csv', format(rep)
 
    #save_results DONT OVERWRITE
    results1.to_csv('results_reference_MOEA_0.csv')
    convergence1.to_csv('convergene_reference_MOEA_0.csv')

