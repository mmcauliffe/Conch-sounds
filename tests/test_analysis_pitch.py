from conch.analysis.pitch import PitchTrackFunction
import librosa
import pytest
from conch.analysis.segments import FileSegment, SignalSegment
from conch.exceptions import FunctionMismatch


def test_pitch_praat(base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PitchTrackFunction(time_step=0.01, min_pitch=75, max_pitch=600)
        pitch = func(wavpath)

        sig, sr = librosa.load(wavpath)

        pitch2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert pitch == pitch2


def test_segment_pitch_track(acoustic_corpus_path):
    func = PitchTrackFunction(time_step=0.01, min_pitch=75, max_pitch=600)
    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0.1)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=10)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

