import os

from ..praat import PraatAnalysisFunction

from pyraat.parse_outputs import parse_track_script_output


def track_pulse_parse_output(text):
    track_text = []
    pulse_text = []
    blank_count = 0
    add_track = True
    for line in text.splitlines():
        line = line.strip()
        if line:
            blank_count = 0
        else:
            blank_count += 1
        if blank_count > 1:
            add_track = False
            continue
        if add_track:
            track_text.append(line)
        else:
            pulse_text.append(line)
    track = parse_track_script_output('\n'.join(track_text))
    pulses = []
    for line in pulse_text:
        line = line.strip()
        if not line:
            continue
        pulses.append(float(line))
    return track, pulses


class PraatPitchTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01, min_pitch=75, max_pitch=600, silence_threshold=0.03,
                 voicing_threshold=0.45, octave_cost=0.01, octave_jump_cost=0.35, voiced_unvoiced_cost=0.14,
                 with_pulses=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if with_pulses:
            script = os.path.join(script_dir, 'pitch_track_with_pulses.praat')
        else:
            script = os.path.join(script_dir, 'pitch_track.praat')
        arguments = [time_step, min_pitch, max_pitch, silence_threshold, voicing_threshold, octave_cost,
                     octave_jump_cost, voiced_unvoiced_cost]
        super(PraatPitchTrackFunction, self).__init__(script, praat_path, arguments)
        if with_pulses:
            self._function._output_parse_function = track_pulse_parse_output


class PraatSegmentPitchTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01, min_pitch=75, max_pitch=600, silence_threshold=0.03,
                 voicing_threshold=0.45, octave_cost=0.01, octave_jump_cost=0.35, voiced_unvoiced_cost=0.14,
                 with_pulses=False):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        if with_pulses:
            script = os.path.join(script_dir, 'pitch_track_with_pulses_segment.praat')
        else:
            script = os.path.join(script_dir, 'pitch_track_segment.praat')
        arguments = [time_step, min_pitch, max_pitch, silence_threshold, voicing_threshold, octave_cost,
                     octave_jump_cost, voiced_unvoiced_cost]
        super(PraatSegmentPitchTrackFunction, self).__init__(script, praat_path, arguments)
        if with_pulses:
            self._function._output_parse_function = track_pulse_parse_output
