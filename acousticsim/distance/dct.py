
from scipy.fftpack import dct
from scipy.spatial.distance import euclidean

def dct_distance(source,target,norm=True,numC=3):
    numBands = source.shape[1]
    distVal = 0
    for i in range(numBands):
        source_dct = dct(source[:,i],norm='ortho')
        if norm:
            source_dct = source_dct[1:]
        source_dct = source_dct[0:numC]
        target_dct = dct(target[:,i],norm='ortho')
        if norm:
            target_dct = target_dct[1:]
        target_dct = target_dct[0:numC]
        if len(target_dct) < numC:
            source_dct = source_dct[:len(target_dct)]
        if len(source_dct) < numC:
            target_dct = target_dct[:len(source_dct)]
        distVal += euclidean(source_dct,target_dct)
    return distVal/numBands
        
