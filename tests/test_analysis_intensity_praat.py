from conch.analysis.intensity.praat import PraatIntensityTrackFunction, PraatSegmentIntensityTrackFunction
import librosa
import pytest
import shutil

from conch.analysis.segments import FileSegment, SignalSegment
from conch.exceptions import FunctionMismatch


def test_intensity_praat(praatpath, base_filenames):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatIntensityTrackFunction(praat_path=praatpath, time_step=0.01)
        pitch = func(wavpath)

        sig, sr = librosa.load(wavpath)

        pitch2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        #assert pitch == pitch2



def test_segment_pitch_track_praat(praatpath, base_filenames):
    praat_path = shutil.which("praat")
    if praat_path is None:
        pytest.skip("No Praat")
    for f in base_filenames:
        if f != 'acoustic_corpus':
            continue
        wavpath = f + '.wav'
        func = PraatSegmentIntensityTrackFunction(praat_path=praatpath, time_step=0.01)
        segment = FileSegment(wavpath, 2.142, 2.245, 0, padding=0.1)
        pitch = func(segment)
        assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

        segment = FileSegment(wavpath, 2.142, 2.245, 0, padding=10)
        pitch = func(segment)
        assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

        segment = FileSegment(wavpath, 2.142, 2.245, 0, padding=0)
        pitch = func(segment)
        assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

        sig, sr = librosa.load(wavpath)

        with pytest.raises(FunctionMismatch):
            formants2 = func(SignalSegment(sig, sr))