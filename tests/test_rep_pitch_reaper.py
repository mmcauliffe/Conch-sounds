

from acousticsim.representations.reaper import to_pitch_reaper

from numpy.testing import assert_array_almost_equal



def test_reaper(noise_path, y_path, reaperpath):

    rep = to_pitch_reaper(noise_path, reaper = reaperpath, time_step = 0.01, freq_lims = (75,600))
    assert(rep.to_array().mean() == -1)

    rep = to_pitch_reaper(y_path, reaper = reaperpath, time_step = 0.01, freq_lims = (75,600))
    print(rep.to_array())
    assert(rep.to_array()[1:-1].mean() - 98.)
