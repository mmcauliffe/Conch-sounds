from conch.distance.dct import DctFunction


def test_dct(reps_for_distance):
    source, target = reps_for_distance
    func = DctFunction()
    dist = func(source, target)
