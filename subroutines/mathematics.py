#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
from numba import njit

################ for fun ######################
def starsss(func):
    def inner(*args, **kwargs):
        print("*" * 30)
        func(*args, **kwargs)
        print("*" * 30)
    return inner

def percentsss(func):
    def inner(*args, **kwargs):
        print("%" * 30)
        func(*args, **kwargs)
        print("%" * 30)
    return inner
################ for fun ######################

##############################################################################

@njit
def gaussian(p, x):
    """
    Returns a scaled Gaussian function for visual comparison of the measured data
    """
    mu, sigma, A = p
    return A/(np.sqrt(2*np.pi)*sigma)*np.exp(-0.5*(x-mu)**2/sigma**2)

@njit 
def poissonian(p, x):
    x = np.floor(x)
    fac = numba_factorial(x)
    return p**x / fac * np.exp(-p)

### beware of integer overflow!!!!!!!!
# @njit
def numba_factorial(x):
    fac = 1
    for i in range(1, x+1):
        fac *= i
    return int(fac)

# @njit 
def numba_stirling2(n, k):
    reciprocal = numba_factorial(k)
    summation = 0

    if k > n:
        return 0

    else:
        for i in range(k+1):
            value = (-1)**i * numba_combination(k, i) * (k - i)**n
            summation += value
        return summation / reciprocal



# @njit
def numba_combination(n, m):
    '''
    D = number of possible detection events
    N = number of possible photons detected at each D
    '''
    if n >= m:

        combination = int(numba_factorial(n) / (numba_factorial(m) * numba_factorial(n - m)))
    else: 
        combination = 0
    
    if combination < 0: print(numba_factorial(n), (numba_factorial(m) * numba_factorial(n - m)),' combi')
    return combination



##############################################################################
@njit
def numba_histogram(a, bins):
    hist = np.zeros((bins,), dtype=np.intp)
    bin_edges = get_bin_edges(a, bins)

    for x in a.flat:
        bin = compute_bin(x, bin_edges)
        if bin is not None:
            hist[int(bin)] += 1

    return hist, bin_edges

@njit
def get_bin_edges(a, bins):
    bin_edges = np.zeros((bins+1,), dtype=np.float64)
    a_min = a.min()
    a_max = a.max()
    delta = (a_max - a_min) / bins
    for i in range(bin_edges.shape[0]):
        bin_edges[i] = a_min + i * delta

    bin_edges[-1] = a_max  # Avoid roundoff error on last point
    return bin_edges


@njit
def compute_bin(x, bin_edges):
    # assuming uniform bins for now
    n = bin_edges.shape[0] - 1
    a_min = bin_edges[0]
    a_max = bin_edges[-1]

    # special case to mirror NumPy behavior for last bin
    if x == a_max:
        return n - 1 # a_max always in last bin

    bin = int(n * (x - a_min) / (a_max - a_min))

    if bin < 0 or bin >= n:
        return None
    else:
        return bin

##############################################################################3

def tag_fourchannel_splice(tags, channels, commonfloor = False, save = False):

    
    spliced_channels = splice_aux(tags, channels)
    if save:
        now = datetime.now()
        dt_string = now.strftime("%d%m%Y_%H_%M_%S")

        for index, channel in enumerate(spliced_channels):
            np.save('output/channel{}_tags_{}'.format(index+1, dt_string), channel)

    if commonfloor: 
        min_candidates = []
        for channel in spliced_channels:
            if len(channel) > 0:
                min_candidates.append(np.min(channel))

        mintag = min(min_candidates)

        output = []
        for channel in spliced_channels:
            output.append(np.insert(channel, 0, mintag))
    
    print(len(output))
    return output


@njit
def splice_aux(tags, channels):
    channel1 = []
    channel2 = []
    channel3 = []
    channel4 = []

    for index, tag in enumerate(tags):

        if channels[index] == 1.:
            channel1.append(tag)
        if channels[index] == 2.:
            channel2.append(tag)
        if channels[index] == 3.:
            channel3.append(tag)
        if channels[index] == 4.:
            channel4.append(tag)

    channel1 = np.array(channel1)
    channel2 = np.array(channel2)
    channel3 = np.array(channel3)
    channel4 = np.array(channel4)
    
    return channel1, channel2, channel3, channel4
##############################################################################

