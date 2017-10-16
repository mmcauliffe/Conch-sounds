from conch.analysis.pitch.reaper import ReaperPitchTrackFunction
from statistics import mean
from scipy.io import wavfile

from conch.analysis.segments import FileSegment, SignalSegment


def test_pitch_reaper(noise_path, y_path, reaperpath):
    func = ReaperPitchTrackFunction(reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600)
    pitch = func(noise_path)
    assert (mean(x['F0'] for x in pitch.values()) == -1)

    sr, sig = wavfile.read(noise_path)

    pitch2 = func(SignalSegment(sig, sr))

    #assert pitch == pitch2

    pitch = func(y_path)
    assert (mean(x['F0'] for x in pitch.values()) - 98.514) < 0.001

    sr, sig = wavfile.read(y_path)

    pitch2 = func(SignalSegment(sig, sr))
    #assert pitch == pitch2


def test_pitch_reaper_pulses(noise_path, y_path, reaperpath):
    func = ReaperPitchTrackFunction(reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600, with_pulses=True)
    pitch, pulses = func(noise_path)
    assert (mean(x['F0'] for x in pitch.values()) == -1)

    sr, sig = wavfile.read(noise_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))

    #assert pitch == pitch2

    pitch, pulses = func(y_path)
    assert (mean(x['F0'] for x in pitch.values()) - 98.514) < 0.001

    sr, sig = wavfile.read(y_path)

    pitch2, pulses2 = func(SignalSegment(sig, sr))
    #assert pitch == pitch2
