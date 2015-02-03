
from scipy.fftpack import dct
from scipy.spatial.distance import euclidean

def dct_distance(rep_one,rep_two,norm=True,numC=3):
    rep_one = rep_one.to_array()
    rep_two = rep_two.to_array()
    numBands = rep_one.shape[1]
    distVal = 0
    for i in range(numBands):
        source_dct = dct(rep_one[:,i],norm='ortho')
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

