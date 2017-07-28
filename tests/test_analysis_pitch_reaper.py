import pytest
from acousticsim.analysis.pitch.reaper import file_to_pitch_reaper
from statistics import mean


def test_reaper(noise_path, y_path, reaperpath):
    rep = file_to_pitch_reaper(noise_path, reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600)
    assert (mean(x['F0'] for x in rep.values()) == -1)

    rep = file_to_pitch_reaper(y_path, reaper_path=reaperpath, time_step=0.01, min_pitch=75, max_pitch=600)
    assert (mean(x['F0'] for x in rep.values())  - 98.)
