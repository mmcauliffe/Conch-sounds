
from acousticsim.processing.speech_detect import SpeechClassifier

def test_sc(base_filenames, do_long_tests):
    if not do_long_tests:
        return
    sc = SpeechClassifier('timit')
    for f in base_filenames:
        wavpath = f + '.wav'
        p = sc.predict_file(wavpath, norm_amp = False,
                        alg = 'bayes',use_segments=False)
