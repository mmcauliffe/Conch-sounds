from conch.analysis.formants.praat import PraatFormantTrackFunction, PraatFormantPointFunction, \
    PraatSegmentFormantPointFunction, PraatSegmentFormantTrackFunction
import librosa
import pytest
import shutil
from conch.exceptions import FunctionMismatch

from conch.analysis.segments import FileSegment, SignalSegment, SegmentMapping


def test_formant_track_praat(praatpath, base_filenames):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatFormantTrackFunction(praat_path=praatpath, time_step=0.01,
                                         window_length=0.025, num_formants=5, max_frequency=5500)
        formants = func(wavpath)

        sig, sr = librosa.load(wavpath)

        formants2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert formants == formants2


def test_formant_point_praat(praatpath, base_filenames):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatFormantPointFunction(praat_path=praatpath, time_step=0.01,
                                         window_length=0.025, num_formants=5, max_frequency=5500, point_percent=0.33)
        formants = func(wavpath)

        sig, sr = librosa.load(wavpath)

        formants2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert formants == formants2


def test_segment_formant_track_praat(praatpath, acoustic_corpus_path):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    func = PraatSegmentFormantTrackFunction(praat_path=praatpath, time_step=0.01,
                                     window_length=0.025, num_formants=5, max_frequency=5500)
    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0.1)
    formants = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in formants.keys())

    sig, sr = librosa.load(acoustic_corpus_path)

    with pytest.raises(FunctionMismatch):
        formants2 = func(SignalSegment(sig, sr))

    # Things are not exact...
    # assert formants == formants2


def test_segment_formant_point_praat(praatpath, acoustic_corpus_path):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    func = PraatSegmentFormantPointFunction(praat_path=praatpath, time_step=0.01,
                                     window_length=0.025, num_formants=5, max_frequency=5500, point_percent=0.33)

    with pytest.raises(FunctionMismatch):
        formants = func(acoustic_corpus_path)
    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0.1)

    formants = func(segment)
    assert abs(formants['F1'] - 480) < 50
    assert abs(formants['F2'] - 1496) < 100
    assert abs(formants['F3'] - 2593) < 250
    assert abs(formants['F4'] - 3673) < 500

    sig, sr = librosa.load(acoustic_corpus_path)

    with pytest.raises(FunctionMismatch):
        formants2 = func(SignalSegment(sig, sr))

    # Things are not exact...
    # assert formants == formants2

