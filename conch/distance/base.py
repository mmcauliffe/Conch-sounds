import numpy as np
from scipy.spatial.distance import euclidean


def track_dict_to_array(data):
    times = sorted(data.keys())
    ex = next(iter(data.values()))
    try:
        frame_len = len(ex)
    except ValueError:
        frame_len = 1

    output = np.zeros((len(times), frame_len))
    for i, t in enumerate(times):
        d = data[t]
        if isinstance(data[t], dict):
            d = [v for k,v in sorted(data[t].items())]
        output[i, :] = [x if x else 0 for x in d]
    return output


class DistanceFunction(object):
    def __init__(self):
        self._function = euclidean
        self.arguments = []

    def __call__(self, first_arg, second_arg):
        if isinstance(first_arg, dict):
            if any(isinstance(x, (float,int)) for x in first_arg.keys()):
                first_arg = track_dict_to_array(first_arg)

        if isinstance(second_arg, dict):
            if any(isinstance(x, (float,int)) for x in second_arg.keys()):
                second_arg = track_dict_to_array(second_arg)

        return self._function(first_arg, second_arg, *self.arguments)
