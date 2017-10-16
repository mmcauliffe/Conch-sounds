import warnings
from .helper import fix_time_points, ASTemporaryWavFile


class BaseAnalysisFunction(object):
    def __init__(self):
        self.uses_segments = False
        self._function = print

    def __call__(self, *args, **kwargs):
        first_arg = args[0]
        args = args[1:]
        if isinstance(first_arg, (tuple, list)):
            #if not self.uses_segments:
            #    warnings.warn('This function is not optimized for segment')
            signal, sr = first_arg[:2]
            begin, padding = None, None
            if len(first_arg) > 2:
                begin = first_arg[2]
                if len(first_arg) > 3:
                    padding = first_arg[3]
            with ASTemporaryWavFile(signal, sr) as wav_path:
                output = self._function(wav_path, self.reaper_path, *args)
            if begin is not None:
                duration = signal.shape[0] / sr
                output = fix_time_points(output, begin, padding, duration)
            return output

        return self._function(first_arg, self.reaper_path, *args)