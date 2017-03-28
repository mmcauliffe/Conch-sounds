
import pytest

from acousticsim.main import analyze_directory
from acousticsim.clustering.network import ClusterNetwork

slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)

#@slow
def test_clustering(soundfiles_dir, call_back):
    kwargs = {'rep': 'mfcc','win_len': 0.025,
                'time_step': 0.01, 'num_coeffs': 13,
                'freq_lims': (0,8000),'return_rep':True}
    scores,reps = analyze_directory(soundfiles_dir, call_back = call_back,**kwargs)
    kwargs['cache'] = reps
    cn = ClusterNetwork(reps)

    cn.cluster(scores,'complete',False)

    cn.cluster(scores, 'affinity', False)

    cn.cluster(scores, 'affinity', True)
