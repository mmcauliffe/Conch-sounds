from numpy import zeros, inf, ones
import numpy as np
from scipy.spatial.distance import euclidean
import operator

from .base import DistanceFunction


class DtwFunction(DistanceFunction):
    def __init__(self, norm=True):
        super(DtwFunction, self).__init__()
        self._function = dtw_distance
        self.arguments = [norm]


def dtw_distance(rep_one, rep_two, norm=True):
    """Computes the distance between two representations with the same
    number of filters using Dynamic Time Warping.

    Parameters
    ----------
    rep_one : 2D array
        First representation to compare. First dimension is time in frames
        or samples and second dimension is the features.
    rep_two : 2D array
        Second representation to compare. First dimension is time in frames
        or samples and second dimension is the features.

    Returns
    -------
    float
        Distance of dynamically time warping `rep_one` to `rep_two`.

    """
    if not isinstance(rep_one, np.ndarray):
        rep_one = rep_one.to_array()
    if not isinstance(rep_two, np.ndarray):
        rep_two = rep_two.to_array()
    assert (rep_one.shape[1] == rep_two.shape[1])
    distMat = generate_distance_matrix(rep_one, rep_two)
    return regularDTW(distMat, norm=norm)


def generate_distance_matrix(source, target, weights=None):
    """Generates a local distance matrix for use in dynamic time warping.

    Parameters
    ----------
    source : 2D array
        Source matrix with features in the second dimension.
    target : 2D array
        Target matrix with features in the second dimension.

    Returns
    -------
    2D array
        Local distance matrix.

    """
    if weights is None:
        weights = ones((source.shape[1], 1))
    sLen = source.shape[0]
    tLen = target.shape[0]
    distMat = zeros((sLen, tLen))
    for i in range(sLen):
        for j in range(tLen):
            distMat[i, j] = euclidean(source[i, :], target[j, :])
    return distMat


def regularDTW(distMat, norm=True):
    """Use a local distance matrix to perform dynamic time warping.

    Parameters
    ----------
    distMat : 2D array
        Local distance matrix.

    Returns
    -------
    float
        Total unweighted distance of the optimal path through the
        local distance matrix.

    """
    sLen, tLen = distMat.shape
    totalDistance = zeros((sLen, tLen))
    totalDistance[0:sLen, 0:tLen] = distMat

    minDirection = zeros((sLen, tLen))

    for i in range(1, sLen):
        totalDistance[i, 0] = totalDistance[i, 0] + totalDistance[i - 1, 0]

    for j in range(1, tLen):
        totalDistance[0, j] = totalDistance[0, j] + totalDistance[0, j - 1]

    for i in range(1, sLen):
        for j in range(1, tLen):
            # direction,minPrevDistance = min(enumerate([totalDistance[i,j],totalDistance[i,j+1],totalDistance[i+1,j]]), key=operator.itemgetter(1))
            # totalDistance[i+1,j+1] = totalDistance[i+1,j+1] + minPrevDistance
            # minDirection[i,j] = direction
            minDirection[i, j], totalDistance[i, j] = min(
                enumerate([totalDistance[i - 1, j - 1] + 2 * totalDistance[i, j],
                           totalDistance[i - 1, j] + totalDistance[i, j],
                           totalDistance[i, j - 1] + totalDistance[i, j]]), key=operator.itemgetter(1))
    if norm:
        return totalDistance[sLen - 1, tLen - 1] / (sLen + tLen)
    return totalDistance[sLen - 1, tLen - 1]
