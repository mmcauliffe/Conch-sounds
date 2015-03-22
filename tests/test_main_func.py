import unittest

import os
from acousticsim.main import (acoustic_similarity_mapping,
                                        acoustic_similarity_directories,
                                        analyze_directory)


TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]


def test_analyze_directory(call_back):
    kwargs = {'rep': 'mfcc','win_len': 0.025,
                'time_step': 0.01, 'num_coeffs': 13,
                'freq_lims': (0,8000),'return_rep':True,
                'use_multi':True}
    scores,reps = analyze_directory(TEST_DIR, call_back = call_back,**kwargs)
