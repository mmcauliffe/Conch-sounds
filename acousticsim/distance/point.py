
from scipy.spatial.distance import euclidean
import numpy as np

def point_distance(rep_one, rep_two, point_one, point_two):
    one_val = rep_one[point_one]
    if one_val is None:
        one_val = 0.0
    if not isinstance(one_val,float) and isinstance(one_val[0],tuple):
        one_val = [x[0] for x in one_val]
    two_val = rep_two[point_two]
    if two_val is None:
        two_val = 0.0
    if not isinstance(one_val,float) and isinstance(one_val[0],tuple):
        two_val = [x[0] for x in two_val]
    dist = euclidean(np.array(one_val), np.array(two_val))
    return dist

def vowel_midpoint_distance(rep_one, rep_two):
    if len(rep_one.vowel_times.keys()) != 1 or len(rep_two.vowel_times.keys()) != 1:
        print(rep_one['filename'])
        print(rep_one.vowel_times)
        print(rep_two['filename'])
        print(rep_two.vowel_times)
        raise(ValueError)
    assert(len(rep_one.vowel_times.keys()) == len(rep_two.vowel_times.keys()))
    dist = 0
    one_times = sorted(rep_one.vowel_times.keys())
    two_times = sorted(rep_two.vowel_times.keys())
    for i,v in enumerate(one_times):
        vow_begin, vow_end = v
        one_point = vow_begin + ((vow_end - vow_begin)/2)
        one_val = rep_one[one_point]
        if one_val is None:
            print(rep_one['filename'])
            print(vow_begin,vow_end)
            print(one_point)
            print(sorted(rep_one._rep.keys()))
            raise(ValueError)
        vow_begin, vow_end = two_times[i]
        two_point = vow_begin + ((vow_end - vow_begin)/2)
        two_val = rep_two[two_point]
        if two_val is None:
            print(rep_two['filename'])
            print(vow_begin,vow_end)
            print(two_point)
            print(sorted(rep_two._rep.keys()))
            raise(ValueError)
        #if not isinstance(one_val,(list,np.array)):
        #    one_val = list(one_val)
        #if not isinstance(two_val,(list,np.array)):
        #    two_val = list(two_val)
        #print(one_val)
        #print(np.array(one_val))
        #print(two_val)
        #print(np.array(two_val))
        dist += euclidean(np.array(one_val), np.array(two_val))
    #print(dist)
    #raise(ValueError)
    return dist / len(rep_one.vowel_times.keys())


def vowel_third_distance(rep_one, rep_two):
    if len(rep_one.vowel_times.keys()) < 1 or len(rep_two.vowel_times.keys()) < 1:
        print(rep_one['filename'])
        print(rep_one.vowel_times)
        print(rep_two['filename'])
        print(rep_two.vowel_times)

        raise(ValueError)
    assert(len(rep_one.vowel_times.keys()) == len(rep_two.vowel_times.keys()))
    dist = 0
    one_times = sorted(rep_one.vowel_times.keys())
    two_times = sorted(rep_two.vowel_times.keys())
    for i,v in enumerate(one_times):
        vow_begin, vow_end = v
        one_point = vow_begin + ((vow_end - vow_begin)/3)
        vow_begin, vow_end = two_times[i]
        two_point = vow_begin + ((vow_end - vow_begin)/3)
        one_val = rep_one[one_point]
        #if not isinstance(one_val,list):
        #    one_val = list(one_val)
        two_val = rep_two[two_point]
        #if not isinstance(two_val,list):
        #    two_val = list(two_val)

        dist += euclidean(np.array(one_val), np.array(two_val))
    return dist / len(rep_one.vowel_times.keys())
