from conch.analysis.autovot import AutoVOTAnalysisFunction
import librosa
from statistics import mean
import wave
import pytest
from conch.analysis.segments import SegmentMapping
from conch import analyze_segments


def test_autovot(autovot_filenames, autovot_markings, autovot_correct_times):
    mapping = SegmentMapping()
    for filename in autovot_filenames:
        with wave.open(filename,'r') as f: 
            length = f.getnframes() / float(f.getframerate())
        mapping.add_file_segment(filename, 0, length, channel=0, vot_marks=autovot_markings[filename])
    func = AutoVOTAnalysisFunction(min_vot_length=5, max_vot_length=100)
    output = analyze_segments(mapping, func, multiprocessing=False)
    output_l = sorted([output[x][0] for x in output], key=lambda x: x[0])
    autovot_correct_times.sort(key= lambda x: x[0])
    for o, truth in zip(output_l, autovot_correct_times):
        assert o == truth

