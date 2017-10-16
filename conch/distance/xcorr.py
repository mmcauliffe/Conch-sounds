import numpy as np
from numpy import log, sqrt, sum, correlate, argmax

from .base import DistanceFunction


class XcorrFunction(DistanceFunction):
    def __init__(self):
        super(XcorrFunction, self).__init__()
        self._function = xcorr_distance


def xcorr_distance(rep_one, rep_two):
    if not isinstance(rep_one, np.ndarray):
        rep_one = rep_one.to_array()
    if not isinstance(rep_two, np.ndarray):
        rep_two = rep_two.to_array()
    assert (rep_one.shape[1] == rep_two.shape[1])
    length_diff = rep_one.shape[0] - rep_two.shape[0]
    if length_diff > 0:
        longer_rep = rep_one
        shorter_rep = rep_two
    else:
        longer_rep = rep_two
        shorter_rep = rep_one
    num_bands = longer_rep.shape[1]
    match_sum = 0
    for i in range(num_bands):
        longer_band = longer_rep[:, i]
        denominator = sqrt(sum(longer_band ** 2))
        if denominator != 0:
            longer_band = longer_band / denominator
        shorter_band = shorter_rep[:, i]
        denominator = sqrt(sum(shorter_band ** 2))
        if denominator != 0:
            shorter_band = shorter_band / denominator
        temp = correlate(longer_band, shorter_band, mode='valid')
        match_sum += temp
    max_index = argmax(match_sum)
    match_value = abs(match_sum[max_index] / num_bands)
    return 1 / match_value

