# -*- coding: utf-8 -*-
"""
Created on Wed Mar 21 17:34:11 2018

@author: ciullo
"""

import numpy as np
from operator import add
from ema_workbench import (Model, CategoricalParameter,
                           ScalarOutcome, TimeSeriesOutcome, IntegerParameter, RealParameter)

from dike_model_function_V2_0 import (DikeNetwork,DikeNetworkTS)  # @UnresolvedImport

def sum_time_series(*args):
    a = np.zeros(len(args[0]))
    for b in args:
        a = list(map(add,a,b))
    return a

def sum_over(*args):
    print(sum(args))
    return sum(args)

def get_model_for_actor_problem_formulation(problem_formulation_id,outcome_type='time_series', direction = ScalarOutcome.MINIMIZE):
    ''' Prepare DikeNetwork in a way it can be input in the EMA-workbench.
    Specify uncertainties, levers and problem formulation.
    '''
    # Load the model:
    if outcome_type == 'time_series':
        function = DikeNetworkTS()
    elif outcome_type == 'scalar':
        function = DikeNetwork()
    else:
        raise TypeError("unknown outcome_type indentifier: try 'time_series' or 'scalar'")
        
    # workbench model:
    dike_model = Model('dikesnet', function=function)

    # Uncertainties and Levers:
    # Specify uncertainties range:
    Real_uncert = {'Bmax': [30, 350], 'pfail': [0, 1]}  # m and [.]
    # breach growth rate [m/day]
    cat_uncert_loc = {'Brate': (1., 1.5, 10)}

    cat_uncert = {'discount rate {}'.format(n): (1.5, 2.5, 3.5, 4.5)
                    for n in function.planning_steps}

    #treat all levers as uncertainties
    dike_lev = {'A.0_ID flood wave shape': [0, 132], 'DikeIncrease': [0, 10], 'EWS_DaysToThreat': [0, 4]}

    # Series of five Room for the River projects:
    rfr_lev = ['{}_RfR'.format(project_id) for project_id in range(0, 5)]

    uncertainties = []
    levers = []

    for uncert_name in cat_uncert.keys():
        categories = cat_uncert[uncert_name]
        uncertainties.append(CategoricalParameter(uncert_name, categories))

    # RfR levers can be either 0 (not implemented) or 1 (implemented)
    for lev_name in rfr_lev:
        for n in function.planning_steps:
            lev_name_ = '{} {}'.format(lev_name, n)
            uncertainties.append(IntegerParameter(lev_name_, 0, 1))

    # Early Warning System lever
    for lev_name in EWS_lev.keys():
        uncertainties.append(IntegerParameter(lev_name, EWS_lev[lev_name][0],
                                       EWS_lev[lev_name][1]))
    
    for dike in function.dikelist:
        # uncertainties in the form: locationName_uncertaintyName
        for uncert_name in Real_uncert.keys():
            name = "{}_{}".format(dike, uncert_name)
            lower, upper = Real_uncert[uncert_name]
            uncertainties.append(RealParameter(name, lower, upper))

        for uncert_name in cat_uncert_loc.keys():
            name = "{}_{}".format(dike, uncert_name)
            categories = cat_uncert_loc[uncert_name]
            uncertainties.append(CategoricalParameter(name, categories))

        # location-related levers in the form: locationName_leversName
        for lev_name in dike_lev.keys():
            for n in function.planning_steps:
                name = "{}_{} {}".format(dike, lev_name, n)
                uncertainties.append(IntegerParameter(name, dike_lev[lev_name][0],
                                           dike_lev[lev_name][1]))

    # load uncertainties and levers in dike_model:
    dike_model.uncertainties = uncertainties
    dike_model.levers = levers

    # Problem formulations:
    # Outcomes are all costs, thus they have to minimized:
    #direction = ScalarOutcome.MINIMIZE
    #direction = ScalarOutcome.MAXIMIZE #to optimize for perfect storm/worst cases etc
    direction = direction
    
    if outcome_type == 'time_series':
        outcome_names = ['Expected Annual Damage','Dike Investment Costs','Expected Number of Deaths',
                     'RfR Total Costs','Expected Evacuation Costs']

        if problem_formulation_id == 1: # RWS
            dike_model.outcomes.clear()
            temp_outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name))
                                  for dike in function.dikelist for name in [outcome_names[0], outcome_names[2]]]
            temp_outcomes.append(TimeSeriesOutcome('Total Investment Costs',
                                                   variable_name=['{}_Dike Investment Costs'.format(dike)
                                                                 for dike in function.dikelist]+
                                                   ['RfR Total Costs']+
                                                   ['Expected Evacuation Costs'], function=sum_time_series))
            
            dike_model.outcomes = temp_outcomes

        elif problem_formulation_id == 2: # Environmental interest group
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name))
                                  for dike in function.dikelist for name in [outcome_names[0], outcome_names[2]]]

        elif problem_formulation_id == 3: # Transport company 
            pass # ADD SOMETHING ABOUT RIVER FLOW AND DEPTH

        elif problem_formulation_id == 4: # Delta commission
            dike_model.outcomes.clear()
            temp_outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name))
                                  for dike in function.dikelist for name in [outcome_names[0], outcome_names[2]]]
            temp_outcomes.append(TimeSeriesOutcome('Total Investment Costs',
                                                   variable_name=['{}_Dike Investment Costs'.format(dike)
                                                                 for dike in function.dikelist]+
                                                   ['RfR Total Costs']+
                                                   ['Expected Evacuation Costs'], function=sum_time_series))
            
            dike_model.outcomes = temp_outcomes

        elif problem_formulation_id == 5: # GELDERLAND
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name)) for dike in function.dikelist[0:4] 
                              for name in outcome_names[0:3]]

        elif problem_formulation_id == 6: # OVERIJSSEL
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('A.5_{}'.format(name)) for name in outcome_names[0:3]]


        elif problem_formulation_id == 7: # Dike rings 1 and 2
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name)) for dike in function.dikelist[0:2] 
                              for name in outcome_names[0:3]]

        elif problem_formulation_id == 8: # Dike ring 3
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('A.3_{}'.format(name)) for name in outcome_names[0:3]]

        elif problem_formulation_id == 9: # Dike ring 4
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('A.4_{}'.format(name)) for name in outcome_names[0:3]]

        elif problem_formulation_id == 10: # Dike ring 5
            dike_model.outcomes.clear()
            dike_model.outcomes = [TimeSeriesOutcome('A.5_{}'.format(name)) for name in outcome_names[0:3]]
            
        elif problem_formulation_id == 11: # RWS formulation 2 (NOTE: Not different from 1 yet)
            dike_model.outcomes.clear()
            temp_outcomes = [TimeSeriesOutcome('{}_{}'.format(dike,name))
                                  for dike in function.dikelist for name in [outcome_names[0], outcome_names[2]]]
            temp_outcomes.append(TimeSeriesOutcome('Total Investment Costs',
                                                   variable_name=['{}_Dike Investment Costs'.format(dike)
                                                                 for dike in function.dikelist]+
                                                   ['RfR Total Costs']+
                                                   ['Expected Evacuation Costs'], function=sum_time_series))

        else:
            raise TypeError('unknown identifier')
        
    elif outcome_type == 'scalar':
        if problem_formulation_id == 1: # RWS
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                # Gelderland
                ScalarOutcome('Expected Annual Damage Gelderland',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:3] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),
                ScalarOutcome('Dike Investment Costs Gelderland',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:3] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),
                ScalarOutcome('Expected Number of Deaths in Gelderland',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:3] for steps in function.planning_steps],
                              function=sum_over, kind=direction),
                # Overijssel
                ScalarOutcome('Expected Annual Damage Overijssel',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist[3:5] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),
                ScalarOutcome('Dike Investment Costs Overijssel',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist[3:5] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),
                ScalarOutcome('Expected Number of Deaths in Overijssel',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist[3:5] for steps in function.planning_steps],
                              function=sum_over, kind=direction),
                # RfR Total Costs
                ScalarOutcome('RfR Total Costs', variable_name=['RfR Total Costs {}'.format(steps) 
                                                                for steps in function.planning_steps],
                             function=sum_over, kind=direction),
                # Expected Evacuation Costs
                ScalarOutcome('Expected Total Evacuation Costs', variable_name=['Expected Evacuation Costs {}'.format(steps) 
                                                                                for steps in function.planning_steps],
                             function=sum_over, kind=direction)
            ]

        elif problem_formulation_id == 2: # Environmental interest group
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction)]

        elif problem_formulation_id == 3: # Transport company
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Total Investment Costs',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps]+
                              ['RfR Total Costs {}'.format(steps) for steps in function.planning_steps]+
                              ['Expected Evacuation Costs {}'.format(steps) for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction)]

        elif problem_formulation_id == 4: # Delta commission
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Total Investment Costs',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps]+
                              ['RfR Total Costs {}'.format(steps) for steps in function.planning_steps]+
                              ['Expected Evacuation Costs {}'.format(steps) for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction)] 

        elif problem_formulation_id == 5: # GELDERLAND
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A1-4',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist[:-1] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A1-4',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist[:-1] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A1-4',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist[:-1] for steps in function.planning_steps],
                              function=sum_over, kind=direction)]

        elif problem_formulation_id == 6: # OVERIJSSEL
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A5', 
                              variable_name=['A.5_Expected Annual Damage {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A5', 
                              variable_name=['A.5_Dike Investment Costs {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A5', 
                              variable_name=['A.5_Expected Number of Deaths {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction)]


        elif problem_formulation_id == 7: # Dike rings 1 and 2
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A1 and A2',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:2] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A1 and A2',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:2] for steps in function.planning_steps], 
                              function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A1 and A2',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist[0:2] for steps in function.planning_steps],
                              function=sum_over, kind=direction)]

        elif problem_formulation_id == 8: # Dike ring 3
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A3', 
                              variable_name=['A.5_Expected Annual Damage {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A3', 
                              variable_name=['A.5_Dike Investment Costs {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A3', 
                              variable_name=['A.5_Expected Number of Deaths {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction)]

        elif problem_formulation_id == 9: # Dike ring 4
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A4', 
                              variable_name=['A.5_Expected Annual Damage {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A4', 
                              variable_name=['A.5_Dike Investment Costs {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A4', 
                              variable_name=['A.5_Expected Number of Deaths {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction)]

        elif problem_formulation_id == 10: # Dike ring 5
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage A5', 
                              variable_name=['A.5_Expected Annual Damage {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Investment Costs A5', 
                              variable_name=['A.5_Dike Investment Costs {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths in A5', 
                              variable_name=['A.5_Expected Number of Deaths {}'.format(steps) 
                                             for steps in function.planning_steps], function=sum_over, kind=direction)]
            
        elif problem_formulation_id == 11: # Fully disaggregated
            dike_model.outcomes.clear()
            dike_model.outcomes = [
                ScalarOutcome('Expected Annual Damage',
                                variable_name=['{}_Expected Annual Damage {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Total Investment Costs',
                                variable_name=['{}_Dike Investment Costs {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps]+
                              ['RfR Total Costs {}'.format(steps) for steps in function.planning_steps]+
                              ['Expected Evacuation Costs {}'.format(steps) for steps in function.planning_steps],
                                function=sum_over, kind=direction),

                ScalarOutcome('Expected Number of Deaths',
                                variable_name=['{}_Expected Number of Deaths {}'.format(dike, steps) 
                                               for dike in function.dikelist for steps in function.planning_steps],
                                function=sum_over, kind=direction)]

        else:
            raise TypeError('unknown identifier')
            
    else:
        raise TypeError('unknown outcome_type identifier, try "time_series" or "scalar"')
        
    return dike_model, function.planning_steps

if __name__ == '__main__':
    get_model_for_problem_formulation(3)