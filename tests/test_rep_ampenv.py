import os
import pytest

from acousticsim.representations.amplitude_envelopes import Envelopes

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal


def test_filter_coeffs():
    b = [[0.0011, 0, -0.0022, 0, 0.0011],
         [0.0097, 0, -0.0194, 0, 0.0097],
         [0.0741, 0, -0.1482, 0, 0.0741],
         [0.4629, 0, -0.9258, 0, 0.4629]]

    a = [[1.0000, -3.8988, 5.7072, -3.7175, 0.9092],
         [1.0000, -3.6459, 5.0421, -3.1369, 0.7415],
         [1.0000, -2.6224, 2.8816, -1.5936, 0.3927],
         [1.0000, 1.1957, -0.1477, -0.1166, 0.2388], ]


@pytest.mark.xfail
def test_envelope_gen(base_filenames):
    for f in base_filenames:
        print(f)
        wavpath = f + '.wav'
        matpath = f + '_lewandowski_env.mat'
        if not os.path.exists(matpath):
            continue
        m = loadmat(matpath)
        env = Envelopes(wavpath, (80, 7800), 4)
        proc = env.process(debug=True)
        # for i in range(self.num_bands):
        #    denom = sqrt(sum(env[:,i]**2))
        #    env[:,i] = env[:,i]/denom
        assert_array_almost_equal(m['wd1'].reshape((m['wd1'].shape[0],)), proc)
        assert_array_almost_equal(m['env1'], env.to_array())


@pytest.mark.xfail
def test_window_envelope(base_filenames):
    for f in base_filenames:
        print(f)
        wavpath = f + '.wav'
        env = Envelopes(wavpath, (80, 7800), 4)
        env.process()
        env.window_envelopes(0.025, 0.010)
