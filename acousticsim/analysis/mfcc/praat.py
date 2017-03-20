import sys
import os

from ..praat import run_script, read_praat_out

from ..helper import ASTemporaryDirectory, fix_time_points, freq_to_mel


def file_to_mfcc_praat(file_path, praat_path=None, win_len=0.025, time_step=0.01,  min_freq=80, max_freq=7800,
                       num_filters=26, num_coeffs=13, use_power=True, deltas=False):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(script_dir, 'mfcc.praat')

    if praat_path is None:
        praat_path = 'praat'
        if sys.platform == 'win32':
            praat_path += 'con.exe'

    listing = run_script(praat_path, script, file_path, num_coeffs, win_len, time_step, freq_to_mel(max_freq))
    output = read_praat_out(listing)
    return output


def signal_to_mfcc_praat(signal, sr, praat_path=None, win_len=0.025, time_step=0.01,  min_freq=80, max_freq=7800,
                         num_filters=26, num_coeffs=13, use_power=True, deltas=False,
                         begin=None, padding=None):
    with ASTemporaryDirectory(prefix = 'acousticsim') as tempdir:
        t_wav = tempdir.create_temp_file(signal, sr)
        output = file_to_mfcc_praat(t_wav.name, praat_path, num_coeffs, win_len, time_step,max_freq)
    duration = signal.shape[0] / sr
    return fix_time_points(output, begin, padding, duration)