
import unittest
import os
import sys

from acousticsim.representations.mfcc import Mfcc

from scipy.io import loadmat

from numpy.testing import assert_array_almost_equal

TEST_DIR = os.path.abspath('tests/data')

filenames = [os.path.splitext(x)[0] for x in os.listdir(TEST_DIR) if x.endswith('.wav')]

class MfccTest(unittest.TestCase):
    def setUp(self):
        self.numCC = 13
        self.winLen = 0.025
        self.timeStep = 0.01
        self.freq_lims = (0,8000)
        self.num_filters = 20

    def test(self):
        for f in filenames:
            print(f)
            if f.startswith('silence'):
                continue
            wavpath = os.path.join(TEST_DIR,f+'.wav')
            matpath = os.path.join(TEST_DIR,f+'_mfcc.mat')
            if not os.path.exists(matpath):
                continue
            m = loadmat(matpath)
            mfcc = Mfcc(wavpath,self.freq_lims,self.numCC,self.winLen,
                                    self.timeStep,num_filters=self.num_filters,
                                    use_power=True
                                    )
            pspec, aspec = mfcc.process(debug=True)
            #assert_array_almost_equal(m['pspectrum'].T,pspec,decimal=4)
            #assert_array_almost_equal(m['aspectrum'].T,aspec,decimal=4)
            assert_array_almost_equal(m['cepstra'].T,mfcc.to_array())
            #mfcc.segment(0.1)
            #break

if __name__ == '__main__':
    unittest.main()
