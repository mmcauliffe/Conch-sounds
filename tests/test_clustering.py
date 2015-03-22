

from numpy import array,sum,sqrt
from numpy.linalg import norm
import os
import sys

from acousticsim.main import analyze_directory

from acousticsim.clustering.network import ClusterNetwork


from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]


def test_clustering(call_back):
    return
    kwargs = {'rep': 'mfcc','win_len': 0.025,
                'time_step': 0.01, 'num_coeffs': 13,
                'freq_lims': (0,8000),'return_rep':True}
    scores,reps = analyze_directory(TEST_DIR, call_back = call_back,**kwargs)
    print(done)
    kwargs['cache'] = reps
    cn = ClusterNetwork(reps)

    cn.cluster(scores,'complete',False)

    cn.cluster(scores, 'affinity', False)

    cn.cluster(scores, 'affinity', True)
