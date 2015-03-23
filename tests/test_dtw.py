

from acousticsim.distance.dtw import dtw_distance, generate_distance_matrix

def test_dtw_unnorm(reps_for_distance):
    source, target = reps_for_distance
    distmat = generate_distance_matrix(source.to_array(), target.to_array())
    linghelper = dtw_distance(source, target,norm=False)

    r_dtw_output = 31.14363
    assert(abs(r_dtw_output - linghelper) < 0.01)

def test_dtw_norm(reps_for_distance):
    source, target = reps_for_distance
    distmat = generate_distance_matrix(source.to_array(), target.to_array())
    linghelper = dtw_distance(source, target,norm=True)

    r_dtw_output = 3.114363
    assert(abs(r_dtw_output - linghelper) < 0.01)


