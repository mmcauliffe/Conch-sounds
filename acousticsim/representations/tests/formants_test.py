

from numpy import array,sum,sqrt
from numpy.linalg import norm
import unittest
import os
import sys

test_dir = os.path.dirname(os.path.abspath(__file__))
test_path = os.path.split(os.path.split(os.path.split(test_dir)[0])[0])[0]
sys.path.insert(0,test_path)
from acousticsim.representations.formants import LpcFormants
from acousticsim.processing.speech_detect import SpeechClassifier


from numpy.testing import assert_array_almost_equal


TEST_DIR = r'C:\Users\michael\Documents\Testing\acoustic_similarity'

#filenames = ['s01_s0101a_big_910','s01_s0101a_care_1188',
            #'s01_s0101a_chief_831','s01_s0101a_choose_1149',
            #'s01_s0101a_come_340','s01_s0101a_dad_497',
            #'s01_s0101a_good_412','s01_s0101a_hall_99']
filenames = ["101_gnat_posttask",
            "101_lab_baseline",
            "101_blues_posttask",
            "101_clue_posttask",
            "101_flash_baseline"]

filenames = [#'102_cot_baseline',
            #'106_deed_shadowing316'
            #'104_toot_shadowing321'
            #'124_teal_shadowing304'
            #'127_toot_shadowing262'
            '124_boot_baseline'
            #'316_cot'
            #'243_deed'
            #'102_key_shadowing304'
            #'102_key_shadowing274'
            ]

class LpcFormantsTest(unittest.TestCase):
    def setUp(self):
        self.num_formants = 5
        self.max_freq = 5500
        self.win_len = 0.025
        self.time_step = 0.01

    def test_lpc(self):
        sc_101 = SpeechClassifier('new')
        sc_101.train_range(r'C:\Users\michael\Documents\Data\ATI_new\Shadowers\Male\124')
        for f in filenames:
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            print(f)
            formants = LpcFormants(wavpath,self.max_freq, self.num_formants, self.win_len,self.time_step)
            #print(formants.to_array())
            #print(formants.to_array('bandwidth'))
            sc = SpeechClassifier('timit')
            vowels = sc.find_vowels(wavpath, sc_101._ranges, num_vowels = 1, debug = True)
            print(vowels)
            #vnv = sc.predict_file(wavpath,win_len=self.win_len,
                                #time_step=self.time_step, norm_amp = True,
                                #alg = 'bayes',use_segments=False,new_range = sc_101._ranges)

            #print(vnv)
            #raise(ValueError)

if __name__ == '__main__':
    unittest.main()
