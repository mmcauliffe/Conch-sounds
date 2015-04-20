

from acousticsim.representations import Mfcc

def test_sc(concatenated, do_long_tests):
    if not do_long_tests:
        return
    rep = Mfcc(None,freq_lims = (80,8000), num_coeffs=13, win_len=0.025,
                        time_step=0.01, num_filters = 26, use_power = False,
                        attributes=None, deltas = False)
    rep.process(signal = (16000,concatenated))
    rep.segment()

