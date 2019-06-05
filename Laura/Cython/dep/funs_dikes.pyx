# -*- coding: utf-8 -*-
"""
Created on Thu Jul 06 14:51:04 2017

@author: ciullo
"""
import numpy as np

cimport cython
cimport numpy as cnp
from libc.math cimport log, sqrt

ctypedef cnp.float_t DTYPE_t #create shorthand for pandas array of floats

#function is called when iterating over timesteps and nodes
cpdef  dikefailure(bint sb,float inflow,float hriver, 
                                            float hbas,  float hground,bint status_t1,
                                            float Bmax, float Brate,float  simtime, 
                                            float tbreach, float critWL):
    ''' Function establising dike failure as well as flow balance between the
        river and the polder

         inflow = flow coming into the node
         status = if False the dike has not failed yet
         critWL = water level above which we have failure

    '''
    cdef float tbr,h1
    tbr = tbreach
    #    h1 = hriver - hbreach
    #    h2 = (hbas + hground) - hbreach

    # h river is a water level, hbas a water depth
    h1 = hriver - (hground + hbas)

    cdef float breachflow, outflow,failure, B
    cdef bint status_t2
    # if the dike has already failed:
    if status_t1 == True:

        B = Bmax * (1 - np.exp(-Brate * (simtime - tbreach)))

        if h1 > 0:
            breachflow = 1.7 * B * (h1)**1.5

        # h1 <0 ==> no flow:
        else:
            breachflow = 0

        outflow = max(0, inflow - breachflow)
        status_t2 = status_t1

    # if the dike has not failed yet:
    else:

        failure = hriver > critWL
        outflow = inflow
        breachflow = 0
        # if it fails:
        if failure:
            status_t2 = True
            tbr = simtime
        # if it does not:
        else:
            status_t2 = False

    # if effects of hydrodynamic system behaviour have to be ignored:
    if sb == False:
        outflow = inflow

    return outflow, breachflow, status_t2, tbr

#called 6 times in model (all iterated over timesteps/ planning steps/ nodes etc)
def  Lookuplin(MyFile, inputcol, searchcol, inputvalue):
    ''' Linear lookup function '''
    
    #cdef int  minTableValue, maxTableValue
    #cdef float A,B,C,D

    minTableValue = np.min(MyFile[:, inputcol])
    maxTableValue = np.max(MyFile[:, inputcol])

    if inputvalue >= maxTableValue:
        inputvalue = maxTableValue - 0.01
    elif inputvalue < minTableValue:
        inputvalue = minTableValue + 0.01

    A = np.max(MyFile[MyFile[:, inputcol] <= inputvalue, inputcol])
    B = np.min(MyFile[MyFile[:, inputcol] > inputvalue, inputcol])
    C = np.max(MyFile[MyFile[:, inputcol] == A, searchcol])
    D = np.min(MyFile[MyFile[:, inputcol] == B, searchcol])

    #cdef float ouutputvalue
    outputvalue = C - ((D - C) * ((inputvalue - A) / (A - B))) * 1.0

    return outputvalue


def init_node(value, time):
    init = np.repeat(value, len(time)).tolist()
    return init
