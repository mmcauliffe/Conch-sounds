import pytest

from conch import (acoustic_similarity_mapping,
                   acoustic_similarity_directories,
                   analyze_segments,
                   acoustic_similarity_directory, analyze_long_file)

from conch.analysis import MfccFunction, FormantTrackFunction
from conch.distance import DtwFunction
from conch.analysis.segments import SegmentMapping

slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


# @slow
def test_analyze_directory(soundfiles_dir, call_back):
    func = MfccFunction()
    dist_func = DtwFunction(norm=True)
    scores = acoustic_similarity_directory(soundfiles_dir, analysis_function=func, distance_function=dist_func)


def test_analyze_long_file_reaper(acoustic_corpus_path, reaper_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, reaper_func)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))

    output = analyze_long_file(acoustic_corpus_path, segments, reaper_func, padding=0.5)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))


def test_analyze_file_segments_reaper(acoustic_corpus_path, reaper_func):
    mapping = SegmentMapping()
    seg = (acoustic_corpus_path, 1, 2, 0)
    mapping.add_file_segment(*seg)
    output = analyze_segments(mapping, reaper_func)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))

    mapping[0].properties['padding'] = 0.5
    output = analyze_segments(mapping, reaper_func)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))


def test_analyze_long_file_formants(acoustic_corpus_path, formants_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, formants_func)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))
    output = analyze_long_file(acoustic_corpus_path, segments, formants_func, padding=0.5)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))


def test_analyze_long_file_pitch(acoustic_corpus_path, pitch_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, pitch_func)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))
    output = analyze_long_file(acoustic_corpus_path, segments, pitch_func, padding=0.5)
    for k in output.keys():
        print(sorted(output[k].keys()))
        assert (all(x >= 1 for x in output[k].keys()))
        assert (all(x <= 2 for x in output[k].keys()))
