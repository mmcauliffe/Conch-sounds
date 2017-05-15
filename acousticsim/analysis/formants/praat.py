import sys
import os

from ..praat import run_script, read_praat_out

from ..helper import ASTemporaryWavFile, fix_time_points


def signal_to_formants_praat(signal, sr, praat_path=None, num_formants=5, max_freq=5000,
                             time_step=0.01, win_len=0.025,
                             begin=None, padding=None):
    with ASTemporaryWavFile(signal, sr) as wav_path:
        output = file_to_formants_praat(wav_path, praat_path, num_formants, max_freq, time_step, win_len)
    duration = signal.shape[0] / sr
    return fix_time_points(output, begin, padding, duration)


def file_to_formants_praat(file_path, praat_path=None, num_formants=5, max_freq=5000,
                           time_step=0.01, win_len=0.025):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(script_dir, 'formants.praat')

    if praat_path is None:
        praat_path = 'praat'
        if sys.platform == 'win32':
            praat_path += 'con.exe'

    listing = run_script(praat_path, script, file_path, time_step,
                         win_len, num_formants, max_freq)
    output = read_praat_out(listing)
    return output
