

from numpy import array
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,test_path)
from acousticsim.distance.dtw import dtw_distance,generate_distance_matrix
from acousticsim.representations.base import Representation

class DTWTest(unittest.TestCase):
    def setUp(self):
        self.source = Representation(None,None,None)
        self.source.set_rep({1:[2,3,4],
                            2:[5,6,7],
                            3:[2,7,6],
                            4:[1,5,6]})
        self.target = Representation(None,None,None)
        self.target.set_rep({1:[5,6,7],
                            2:[2,3,4],
                            3:[6,8,3],
                            4:[2,7,9],
                            5:[1,5,8],
                            6:[7,4,9]})

    def test_dtw_unnorm(self):
        distmat = generate_distance_matrix(self.source.to_array(), self.target.to_array())
        linghelper = dtw_distance(self.source,self.target,norm=False)

        r_dtw_output = 31.14363
        self.assertTrue(abs(r_dtw_output - linghelper) < 0.01)

    def test_dtw_norm(self):
        distmat = generate_distance_matrix(self.source.to_array(), self.target.to_array())
        linghelper = dtw_distance(self.source,self.target,norm=True)

        r_dtw_output = 3.114363
        self.assertTrue(abs(r_dtw_output - linghelper) < 0.01)


if __name__ == '__main__':
    unittest.main()
