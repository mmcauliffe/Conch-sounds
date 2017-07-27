import sys
import os
from ..praat import run_script, read_praat_out

from ..helper import fix_time_points, ASTemporaryWavFile


def file_to_pitch_praat(file_path, praat_path=None, time_step=0.01, min_pitch=75, max_pitch=600, silence_threshold=0.03,
                        voicing_threshold=0.45, octave_cost=0.01, octave_jump_cost=0.35, voiced_unvoiced_cost=0.14):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    script = os.path.join(script_dir, 'pitch.praat')
    if praat_path is None:
        praat_path = 'praat'
        if sys.platform == 'win32':
            praat_path += 'con.exe'
    listing = run_script(praat_path, script, file_path, time_step, min_pitch, max_pitch, silence_threshold,
                         voicing_threshold, octave_cost, octave_jump_cost, voiced_unvoiced_cost)
    output = read_praat_out(listing)
    return output


def signal_to_pitch_praat(signal, sr, praat_path=None, time_step=0.01, min_pitch=75, max_pitch=600,
                          silence_threshold=0.03, voicing_threshold=0.45, octave_cost=0.01, octave_jump_cost=0.35,
                          voiced_unvoiced_cost=0.14, begin=None, padding=None):
    with ASTemporaryWavFile(signal, sr) as wav_path:
        output = file_to_pitch_praat(wav_path, praat_path, time_step, min_pitch, max_pitch, silence_threshold,
                                     voicing_threshold, octave_cost, octave_jump_cost, voiced_unvoiced_cost)
    duration = signal.shape[0] / sr
    return fix_time_points(output, begin, padding, duration)
