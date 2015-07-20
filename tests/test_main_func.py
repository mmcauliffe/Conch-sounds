

from acousticsim.main import (acoustic_similarity_mapping,
                                        acoustic_similarity_directories,
                                        analyze_directory)


def test_analyze_directory(soundfiles_dir,call_back, do_long_tests):
    if not do_long_tests:
        return
    kwargs = {'rep': 'mfcc','win_len': 0.025,
                'time_step': 0.01, 'num_coeffs': 13,
                'freq_lims': (0,8000),'return_rep':True,
                'use_multi':True}
    scores,reps = analyze_directory(soundfiles_dir, call_back = call_back,**kwargs)
