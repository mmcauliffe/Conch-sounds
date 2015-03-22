

from numpy import array,sum,sqrt
from numpy.linalg import norm
import os
import sys

from acousticsim.processing.speech_detect import SpeechClassifier


from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]



def test_sc():
    sc = SpeechClassifier('new')
    #sc_101.train_range(r'C:\Users\michael\Documents\Data\ATI_new\Shadowers\Male\124')
    #sc = SpeechClassifier('timit')
    #vowels = sc.find_vowels(wavpath, sc_101._ranges, num_vowels = 1, debug = True)
    #print(vowels)
    #vnv = sc.predict_file(wavpath,win_len=self.win_len,
                        #time_step=self.time_step, norm_amp = True,
                        #alg = 'bayes',use_segments=False,new_range = sc_101._ranges)

    #print(vnv)
    #raise(ValueError)
