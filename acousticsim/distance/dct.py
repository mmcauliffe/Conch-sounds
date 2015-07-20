import numpy as np
from scipy.fftpack import dct
from scipy.spatial.distance import euclidean

def dct_distance(rep_one,rep_two,norm=True,numC=3):
    if not isinstance(rep_one, np.ndarray):
        rep_one = rep_one.to_array()
    if not isinstance(rep_two, np.ndarray):
        rep_two = rep_two.to_array()
    assert(rep_one.shape[1] == rep_two.shape[1])
    numBands = rep_one.shape[1]
    distVal = 0
    for i in range(numBands):
        try:
            source_dct = dct(rep_one[:,i],norm='ortho')
        except ValueError:
            print(rep_one)
            raise
        if norm:
            source_dct = source_dct[1:]
        source_dct = source_dct[0:numC]
        target_dct = dct(rep_two[:,i],norm='ortho')
        if norm:
            target_dct = target_dct[1:]
        target_dct = target_dct[0:numC]
        if len(target_dct) < numC:
            source_dct = source_dct[:len(target_dct)]
        if len(source_dct) < numC:
            target_dct = target_dct[:len(source_dct)]
        distVal += euclidean(source_dct,target_dct)
    return distVal/numBands

