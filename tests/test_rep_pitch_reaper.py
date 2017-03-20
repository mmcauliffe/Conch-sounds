
import pytest
from acousticsim.analysis.pitch.reaper import file_to_pitch_reaper

from numpy.testing import assert_array_almost_equal


@pytest.mark.xfail
def test_reaper(noise_path, y_path, reaperpath):

    rep = file_to_pitch_reaper(noise_path, reaper_path = reaperpath, time_step = 0.01, min_pitch=75, max_pitch=600)
    assert(rep.to_array().mean() == -1)

    rep = file_to_pitch_reaper(y_path, reaper_path = reaperpath, time_step = 0.01, min_pitch=75, max_pitch=600)
    print(rep.to_array())
    assert(rep.to_array()[1:-1].mean() - 98.)
