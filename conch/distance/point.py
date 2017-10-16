from scipy.spatial.distance import euclidean
import numpy as np

from .base import DistanceFunction


class PointFunction(DistanceFunction):
    def __init__(self, point_percent=0.33):
        super(PointFunction, self).__init__()
        self.point_percent = point_percent

    def __call__(self, first_arg, second_arg):
        if isinstance(first_arg, dict):
            if any(isinstance(x, (float,int)) for x in first_arg.keys()):
                min_time = min(first_arg.keys())
                max_time = max(first_arg.keys())
                duration = max_time - min_time
                point = min_time + duration * self.point_percent
                key = min(first_arg.keys(), key=lambda x: abs(x - point))

                first_arg = first_arg[key]

        if isinstance(second_arg, dict):
            if any(isinstance(x, (float,int)) for x in second_arg.keys()):
                min_time = min(second_arg.keys())
                max_time = max(second_arg.keys())
                duration = max_time - min_time
                point = min_time + duration * self.point_percent
                key = min(second_arg.keys(), key=lambda x: abs(x - point))

                second_arg = second_arg[key]

        return self._function(first_arg, second_arg, *self.arguments)

