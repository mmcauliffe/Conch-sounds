from conch.analysis.pitch.reaper import ReaperPitchTrackFunction
from statistics import mean
import librosa
import shutil
import pytest

from conch.analysis.segments import FileSegment, SignalSegment


def test_pitch_reaper(noise_path, y_path, reaperpath):
    reaper_path = shutil.which("reaper")
    if reaper_path is None:
        pytest.skip("No Reaper")
    func = ReaperPitchTrackFunction(reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600)
    pitch = func(noise_path)
    assert (mean(x['F0'] for x in pitch.values()) == -1)

    sig, sr = librosa.load(noise_path)

    pitch2 = func(SignalSegment(sig, sr))

    # assert pitch == pitch2

    pitch = func(y_path)
    assert (mean(x['F0'] for x in pitch.values()) - 98.514) < 0.001

    sig, sr = librosa.load(y_path)

    pitch2 = func(SignalSegment(sig, sr))
    # assert pitch == pitch2


def test_pitch_reaper_pulses(noise_path, y_path, reaperpath):
    reaper_path = shutil.which("reaper")
    if reaper_path is None:
        pytest.skip("No Reaper")
    func = ReaperPitchTrackFunction(reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600,
                                    with_pulses=True)
    pitch, pulses = func(noise_path)
    assert (mean(x['F0'] for x in pitch.values()) == -1)

    sig, sr = librosa.load(noise_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))

    # assert pitch == pitch2

    pitch, pulses = func(y_path)
    assert (mean(x['F0'] for x in pitch.values()) - 98.514) < 0.001

    sig, sr = librosa.load(y_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))
    # assert pitch == pitch2


def test_segment_pitch_track(acoustic_corpus_path, reaperpath):
    reaper_path = shutil.which("reaper")
    if reaper_path is None:
        pytest.skip("No Reaper")
    func = ReaperPitchTrackFunction(reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600)
    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0.1)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=10)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())

    segment = FileSegment(acoustic_corpus_path, 2.142, 2.245, 0, padding=0)
    pitch = func(segment)
    assert all(x >= 2.142 and x <= 2.245 for x in pitch.keys())
