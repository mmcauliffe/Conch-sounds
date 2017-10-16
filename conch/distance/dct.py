import numpy as np
from scipy.fftpack import dct
from scipy.spatial.distance import euclidean

from .base import DistanceFunction


class DctFunction(DistanceFunction):
    def __init__(self, norm=True, num_coefficients=3):
        super(DctFunction, self).__init__()
        self._function = dct_distance
        self.arguments = [norm, num_coefficients]


def dct_distance(rep_one, rep_two, norm=True, num_coefficients=3):
    if not isinstance(rep_one, np.ndarray):
        rep_one = rep_one.to_array()
    if not isinstance(rep_two, np.ndarray):
        rep_two = rep_two.to_array()
    assert (rep_one.shape[1] == rep_two.shape[1])
    num_bands = rep_one.shape[1]
    distance = 0
    for i in range(num_bands):
        try:
            source_dct = dct(rep_one[:, i], norm='ortho')
        except ValueError:
            print(rep_one)
            raise
        if norm:
            source_dct = source_dct[1:]
        source_dct = source_dct[0:num_coefficients]
        target_dct = dct(rep_two[:, i], norm='ortho')
        if norm:
            target_dct = target_dct[1:]
        target_dct = target_dct[0:num_coefficients]
        if len(target_dct) < num_coefficients:
            source_dct = source_dct[:len(target_dct)]
        if len(source_dct) < num_coefficients:
            target_dct = target_dct[:len(source_dct)]
        distance += euclidean(source_dct, target_dct)
    return distance / num_bands
