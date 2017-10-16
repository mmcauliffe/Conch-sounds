
from pyraat import PraatAnalysisFunction as PyraatFunction
from .helper import fix_time_points, ASTemporaryWavFile
from ..exceptions import ImproperPraatFunction


class PraatAnalysisFunction(PyraatFunction):
    def __call__(self, *args, **kwargs):
        first_arg = args[0]
        args = args[1:]
        if isinstance(first_arg, (tuple, list)):
            if self.uses_long:
                raise ImproperPraatFunction('Praat scripts using long files shouldn\'t be used with extracted segments.')
            signal, sr = first_arg[:2]
            begin = kwargs.get('begin', None)
            padding = kwargs.get('padding', None)
            with ASTemporaryWavFile(signal, sr) as wav_path:
                output = super(PraatAnalysisFunction, self).__call__(wav_path, *args, **kwargs)
            if begin is not None:
                duration = signal.shape[0] / sr
                output = fix_time_points(output, begin, padding, duration)
            return output

        return super(PraatAnalysisFunction, self).__call__(first_arg, *args, **kwargs)
