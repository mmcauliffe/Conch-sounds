

from acousticsim.distance.dct import dct_distance

def test_dct(reps_for_distance):
    source, target = reps_for_distance

    dist = dct_distance(source, target)


