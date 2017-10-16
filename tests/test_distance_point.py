from conch.distance.point import PointFunction


def test_point_distance(reps_for_distance):
    source, target = reps_for_distance


    expected_distance = 4.582575695
    point_distance = PointFunction(0.33)
    dist = point_distance(source, target)

    #assert (abs(dist - expected_distance) < 0.001)

    point_distance = PointFunction(0.5)
    expected_distance = 3.905124838

    dist = point_distance(source, target)

    #assert (abs(dist - expected_distance) < 0.001)
