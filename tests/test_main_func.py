import unittest

import os
from acousticsim.main import (acoustic_similarity_mapping,
                                        acoustic_similarity_directories)


TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class RuntimeTest(unittest.TestCase):
    def setUp(self):
        self.dir_one_path = os.path.join(TEST_DIR,'dir_one')
        self.dir_two_path = os.path.join(TEST_DIR,'dir_two')
        self.path_mapping = [(os.path.join(TEST_DIR,'s129_air1.wav'),
                            os.path.join(TEST_DIR,'s129_beer1.wav'))]
        self.expected_val = 0.2266

    def test_dir_phon_sim(self):
        return
        match_val = acoustic_similarity_directories(self.dir_one_path, self.dir_two_path)
        self.assertEqual(match_val,self.expected_val)

    def test_mapping_phon_sim(self):
        return
        output_mapping = acoustic_similarity_mapping(self.path_mapping)
        self.assertEqual(output_mapping[0][2],self.expected_val)

if __name__ == '__main__':
    unittest.main()
