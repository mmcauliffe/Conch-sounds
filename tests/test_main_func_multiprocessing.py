import pytest
import shutil
from conch import (analyze_segments,
                   acoustic_similarity_directory, analyze_long_file,
                   )
from conch.main import axb_mapping
from conch.io import load_path_mapping

from conch.analysis import MfccFunction, FormantTrackFunction, PitchTrackFunction, PraatPitchTrackFunction
from conch.distance import DtwFunction
from conch.analysis.segments import SegmentMapping



def test_acoustic_similarity_directories(tts_dir, call_back, praatpath):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    func = PraatPitchTrackFunction(praat_path=praatpath)
    dist_func = DtwFunction(norm=True)
    scores = acoustic_similarity_directory(tts_dir, analysis_function=func, distance_function=dist_func,
                                           call_back=call_back)


def test_acoustic_similarity_directory(soundfiles_dir, call_back):
    func = PitchTrackFunction()
    dist_func = DtwFunction(norm=True)
    scores = acoustic_similarity_directory(soundfiles_dir, analysis_function=func, distance_function=dist_func,
                                           call_back=call_back)


def test_axb_mapping(axb_mapping_path):
    path_mapping = load_path_mapping(axb_mapping_path)
    assert len(path_mapping[0]) == 3
    func = MfccFunction()
    dist_func = DtwFunction(norm=True)
    scores = axb_mapping(path_mapping, func, dist_func)
    print(scores)


def test_analyze_long_file_reaper(acoustic_corpus_path, reaper_func):
    reaper_path = shutil.which("reaper")
    if reaper_path is None:
        pytest.skip("No Reaper")
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

@pytest.mark.xfail
def test_analyze_file_segments_reaper(acoustic_corpus_path, reaper_func):
    reaper_path = shutil.which("reaper")
    if reaper_path is None:
        pytest.skip("No Reaper")
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
