
from acousticsim.representations.base import Representation

import numpy as np


from numpy.testing import assert_array_almost_equal

def test_base(reps_for_distance):
    source, target = reps_for_distance

    assert(source[-1] == None)
    assert(source[20] == None)

    assert_array_almost_equal(source[1,2], np.array([[2,3,4],[5,6,7]]))

    assert_array_almost_equal(source.to_array(), np.array([[2,3,4],
                                                            [5,6,7],
                                                            [2,7,6],
                                                            [1,5,6]]))
