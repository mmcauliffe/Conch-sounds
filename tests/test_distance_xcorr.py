from conch.distance.xcorr import XcorrFunction


def test_xcorr(reps_for_distance):
    source, target = reps_for_distance
    xcorr_distance = XcorrFunction()
    dist = xcorr_distance(source, target)
    expected_sim = 0.71668096914850421
    expected_dist = 1 / expected_sim
    assert (abs(dist - expected_dist) < 0.0001)
