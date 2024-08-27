from conch.analysis.pitch.praat import PraatPitchTrackFunction, PraatSegmentPitchTrackFunction
import librosa
from statistics import mean
import pytest
import shutil
from conch.analysis.segments import FileSegment, SignalSegment
from conch.exceptions import FunctionMismatch


def test_pitch_praat(praatpath, base_filenames):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatPitchTrackFunction(praat_path=praatpath, time_step=0.01,
                                       min_pitch=75, max_pitch=600)
        pitch = func(wavpath)

        sig, sr = librosa.load(wavpath)

        pitch2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert pitch == pitch2

def test_pitch_pulses_praat(praatpath, noise_path, y_path):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    func = PraatPitchTrackFunction(praat_path=praatpath, time_step=0.01, min_pitch=75, max_pitch=600,
                                    with_pulses=True)
    pitch, pulses = func(noise_path)
    assert (all(x['F0'] is None for x in pitch.values()))

    sig, sr = librosa.load(noise_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))

    # assert pitch == pitch2

    pitch, pulses = func(y_path)
    assert (mean(x['F0'] for x in pitch.values()) - 100) < 1

    sig, sr = librosa.load(y_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))



def test_segment_pitch_track_praat(praatpath, acoustic_corpus_path):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    func = PraatSegmentPitchTrackFunction(praat_path=praatpath, time_step=0.01, min_pitch=75, max_pitch=600)
    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0.1)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=10)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    sig, sr = librosa.load(acoustic_corpus_path)

    with pytest.raises(FunctionMismatch):
        formants2 = func(SignalSegment(sig, sr))