from conch.analysis.autovot import AutoVOTAnalysisFunction
import wave
import pytest
import shutil
from conch.analysis.segments import SegmentMapping
from conch import analyze_segments


def test_autovot(acoustic_corpus_path, autovot_markings, classifier_path, autovot_correct_times):
    autovot_path = shutil.which("VotDecode")
    if autovot_path is None:
        pytest.skip("No AutoVOT")
    mapping = SegmentMapping()
    with wave.open(acoustic_corpus_path, 'r') as f: 
        length = f.getnframes() / float(f.getframerate())
    mapping.add_file_segment(acoustic_corpus_path, 0, length, channel=0, vot_marks=autovot_markings)
    func = AutoVOTAnalysisFunction(classifier_to_use=classifier_path, window_min=-30, window_max=30, min_vot_length=5, max_vot_length=100)
    output = analyze_segments(mapping, func, multiprocessing=False)
    output = output[mapping[0]]
    for o, truth in zip(output, autovot_correct_times):
        assert o == truth

