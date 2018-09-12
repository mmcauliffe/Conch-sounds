from conch.analysis.autovot import AutoVOTAnalysisFunction
import librosa
from statistics import mean
import wave
import pytest
from conch.analysis.segments import FileSegment, SignalSegment
from conch.exceptions import FunctionMismatch


def test_pitch_praat(autovot_filenames, autovot_markings):
    mapping = SegmentMapping()
    for filename in autovot_filenames:
        with wave.open(path,'r') as f: 
            length = f.getnframes() / float(f.getframerate)
        mapping.add_file_segment(filename, 0, length, channel=0, vot_marks=autovot_markings[filename])
    func = AutoVOTAnalysisFunction()
    output = analyze_segments(mapping, reaper_func, multiprocessing=False)
