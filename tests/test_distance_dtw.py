from conch.distance.dtw import DtwFunction, generate_distance_matrix


def test_dtw_unnorm(reps_for_distance):
    source, target = reps_for_distance
    dtw = DtwFunction(norm=False)
    linghelper = dtw(source, target)

    r_dtw_output = 31.14363
    assert (abs(r_dtw_output - linghelper) < 0.01)


def test_dtw_norm(reps_for_distance):
    source, target = reps_for_distance
    dtw = DtwFunction(norm=True)
    linghelper = dtw(source, target)

    r_dtw_output = 3.114363
    assert (abs(r_dtw_output - linghelper) < 0.01)
