

from acousticsim.distance.point import point_distance

def test_point_in(reps_for_distance):
    source, target = reps_for_distance

    time_one = 1
    time_two = 5

    expected_distance = 4.582575695

    dist = point_distance(source, target, time_one, time_two)

    assert(abs(dist - expected_distance) < 0.001)

def test_point_between(reps_for_distance):
    source, target = reps_for_distance

    time_one = 1.5
    time_two = 4.5

    expected_distance = 3.905124838

    dist = point_distance(source, target, time_one, time_two)

    assert(abs(dist - expected_distance) < 0.001)

