import librosa
import os
from .helper import fix_time_points, ASTemporaryWavFile
from .segments import FileSegment, SignalSegment
from ..exceptions import FunctionMismatch


def _fix_signal_segment_times(output, segment, begin, padding):
    """A helper function to adjust times for SignalSegment objects, which (unlike FileSegment objects)
    are assumed to have the full padding width available on both sides of the segment."""
    if padding is None:
        padding = 0
    clip_begin = begin - padding
    clip_end = clip_begin + segment.signal.shape[0] / segment.sr
    return fix_time_points(output, clip_begin, begin, clip_end - padding)


def safe_path(path):
    if '~' in path:
        return os.path.expanduser(path)
    return path


class BaseAnalysisFunction(object):
    def __init__(self):
        self._function = print
        self.requires_file = False
        self.requires_segment_as_arg = False
        self.uses_segments = False
        self.point_measure = False
        self.arguments = []

    def __call__(self, segment):
        if isinstance(segment, SignalSegment) and self.requires_file:
            if self.uses_segments:
                raise FunctionMismatch('Cannot analyze a SignalSegment with a function that uses segments.')
            begin, padding = segment['begin'], segment['padding']
            with ASTemporaryWavFile(segment.signal, segment.sr) as wav_path:
                output = self._function(wav_path, *self.arguments)
            if begin is not None and not self.point_measure:
                output = _fix_signal_segment_times(output, segment, begin, padding)
            return output
        elif isinstance(segment, SignalSegment):
            begin, padding = segment['begin'], segment['padding']
            output = self._function(segment.signal, segment.sr, *self.arguments)
            if begin is not None and not self.point_measure:
                output = _fix_signal_segment_times(output, segment, begin, padding)
            return output
        elif isinstance(segment, str) and not self.requires_file:
            signal, sr = librosa.load(safe_path(segment), sr=None)
            return self._function(signal, sr, *self.arguments)
        elif isinstance(segment, FileSegment) and self.requires_segment_as_arg:
            return self._function(segment, *self.arguments)
        elif isinstance(segment, FileSegment) and self.requires_file and not self.uses_segments:
            beg, end = segment.begin, segment.end
            padding = segment['padding']
            if padding:
                beg -= padding
                if beg < 0:
                    beg = 0
                end += padding
            dur = end - beg
            signal, sr = librosa.load(safe_path(segment.file_path), sr=None, mono=False, offset=beg,
                                      duration=dur)
            if len(signal.shape) > 1:
                signal = signal[segment.channel]
            with ASTemporaryWavFile(signal, sr) as wav_path:
                output = self._function(wav_path, *self.arguments)
            if self.point_measure:
                return output
            return fix_time_points(output, beg, segment.begin, segment.end)

        elif isinstance(segment, FileSegment) and not self.requires_file:
            beg, end = segment.begin, segment.end
            padding = segment['padding']
            if padding:
                beg -= padding
                if beg < 0:
                    beg = 0
                end += padding
            dur = end - beg
            signal, sr = librosa.load(safe_path(segment.file_path), sr=None, mono=False, offset=beg,
                                      duration=dur)
            if len(signal.shape) > 1:
                signal = signal[segment.channel]
            output = self._function(signal, sr, *self.arguments)
            if self.point_measure:
                return output
            return fix_time_points(output, beg, segment.begin, segment.end)
        elif isinstance(segment, FileSegment) and self.requires_file and self.uses_segments:
            padding = segment['padding']
            if padding is None:
                padding = 0
            return self._function(safe_path(segment.file_path), segment.begin, segment.end, segment.channel, padding,
                                  *self.arguments)
        elif isinstance(segment, str) and self.uses_segments:
            raise FunctionMismatch('A FileSegment must be specified to analyze using this function')
        return self._function(segment, *self.arguments)
