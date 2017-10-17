import os

from ..praat import PraatAnalysisFunction


class PraatFormantTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formant_track.praat')
        arguments = [time_step, window_length, num_formants, max_frequency]
        super(PraatFormantTrackFunction, self).__init__(script, praat_path, arguments)


class PraatFormantPointFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025, point_percent=0.33):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formant_point.praat')
        arguments = [time_step, window_length, num_formants, max_frequency, point_percent]
        super(PraatFormantPointFunction, self).__init__(script, praat_path, arguments)


class PraatSegmentFormantTrackFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formant_track_segment.praat')
        arguments = [time_step, window_length, num_formants, max_frequency]
        super(PraatSegmentFormantTrackFunction, self).__init__(script, praat_path, arguments)


class PraatSegmentFormantPointFunction(PraatAnalysisFunction):
    def __init__(self, praat_path=None, num_formants=5, max_frequency=5000,
                 time_step=0.01, window_length=0.025, point_percent=0.33):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        script = os.path.join(script_dir, 'formant_point_segment.praat')
        arguments = [time_step, window_length, num_formants, max_frequency, point_percent]
        super(PraatSegmentFormantPointFunction, self).__init__(script, praat_path, arguments)
