

import pytest

from acousticsim.representations.intensity import Intensity

from numpy.testing import assert_array_almost_equal


@pytest.mark.xfail
def test_intensity(base_filenames):
    for f in base_filenames:
        wavpath = f+'.wav'
        intensity = Intensity(wavpath, time_step = 0.01)
        intensity.process()

