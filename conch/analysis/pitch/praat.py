import os

from ..praat import PraatAnalysisFunction


class PraatPitchTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, time_step=0.01, min_pitch=75, max_pitch=600, silence_threshold=0.03,
                 voicing_threshold=0.45, octave_cost=0.01, octave_jump_cost=0.35, voiced_unvoiced_cost=0.14):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'pitch.praat')
        arguments = [time_step, min_pitch, max_pitch, silence_threshold, voicing_threshold, octave_cost,
                     octave_jump_cost, voiced_unvoiced_cost]
        super(PraatPitchTrackFunction, self).__init__(script, praat_path=praat_path, arguments=arguments)
