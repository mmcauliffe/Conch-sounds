import pytest

from acousticsim.main import (acoustic_similarity_mapping,
                              acoustic_similarity_directories,
                              analyze_file_segments,
                              analyze_directory, analyze_long_file)

slow = pytest.mark.skipif(
    not pytest.config.getoption("--runslow"),
    reason="need --runslow option to run"
)


# @slow
def test_analyze_directory(soundfiles_dir, call_back):
    kwargs = {'rep': 'mfcc', 'win_len': 0.025,
              'time_step': 0.01, 'num_coeffs': 13,
              'freq_lims': (0, 8000), 'return_rep': True,
              'use_multi': True}
    scores, reps = analyze_directory(soundfiles_dir, call_back=call_back, **kwargs)


def test_analyze_long_file_reaper(acoustic_corpus_path, reaper_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, reaper_func)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))

    output = analyze_long_file(acoustic_corpus_path, segments, reaper_func, padding=0.5)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))


def test_analyze_file_segments_reaper(acoustic_corpus_path, reaper_func):
    seg = (acoustic_corpus_path, 1, 2, 0)
    segments = [seg]
    output = analyze_file_segments(segments, reaper_func)
    print(sorted(output[seg].keys()))

    assert (all(x >= 1 for x in output[seg].keys()))
    assert (all(x <= 2 for x in output[seg].keys()))

    output = analyze_file_segments(segments, reaper_func, padding=0.5)
    print(sorted(output[seg].keys()))
    assert (all(x >= 1 for x in output[seg].keys()))
    assert (all(x <= 2 for x in output[seg].keys()))

def test_analyze_long_file_formants(acoustic_corpus_path, formants_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, formants_func)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))
    output = analyze_long_file(acoustic_corpus_path, segments, formants_func, padding=0.5)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))


def test_analyze_long_file_pitch(acoustic_corpus_path, pitch_func):
    segments = [(1, 2, 0)]
    output = analyze_long_file(acoustic_corpus_path, segments, pitch_func)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))
    output = analyze_long_file(acoustic_corpus_path, segments, pitch_func, padding=0.5)
    print(sorted(output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))
    assert (all(x >= 1 for x in output[(1, 2, 0)].keys()))
    assert (all(x <= 2 for x in output[(1, 2, 0)].keys()))
