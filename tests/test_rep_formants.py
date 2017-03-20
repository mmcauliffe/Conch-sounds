


from acousticsim.representations.formants import Formants

from numpy.testing import assert_array_almost_equal

def test_lpc(base_filenames):
    for f in base_filenames:
        if f.startswith('silence'):
            continue
        wavpath = f+'.wav'
        print(f)
        formants = Formants(wavpath, max_freq = 5500,
                    num_formants = 5, win_len = 0.025, time_step = 0.01)

