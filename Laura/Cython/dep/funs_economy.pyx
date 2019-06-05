# -*- coding: utf-8 -*-
"""
Created on Sun Oct 29 15:52:12 2017

@author: ciullo
"""
import numpy as np

cimport cython
cimport numpy as cnp
from libc.math cimport log, sqrt

ctypedef cnp.float_t DTYPE_t ##create shorthand for pandas array of floats

#iterated over diknodes and 'steps'
cpdef float cost_fun( float ratio, float c,float b,float lambd, float dikeinit, float dikeincrease):
    ''' Cost of raising the dikes, assuming an exponential function '''

    dikeincrease = dikeincrease * 100  # cm
    dikeinit = dikeinit * 100

    cdef float cost #will numpy .exp still work with cython??

    cost = ((c + b * dikeincrease) * np.exp(lambd * (dikeinit + dikeincrease))) * ratio
    return cost * 1e6


#iterated over dike
cpdef float discount(float amount, float  rate, int n):
    ''' discount function overall a planning period of n years '''

    cdef float factor, disc_amount
    factor = 1 + rate / 100
    disc_amount = amount * 1 / (np.repeat(factor, n)**(range(1, n + 1)))
    return disc_amount

#If a breach occurs, iterate over every node
#check that both of these are indeed ints !!
cpdef float cost_evacuation(int N_evacuated, int days_to_threat):
    # if days to threat is zero, then no evacuation happens, costs are zero

    cdef float cost
    cost = N_evacuated * 22 * (days_to_threat + 3) * (int(days_to_threat > 0))
    return cost
