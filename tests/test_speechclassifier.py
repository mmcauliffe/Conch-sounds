
from acousticsim.processing.speech_detect import SpeechClassifier

def test_sc(base_filenames):
    sc = SpeechClassifier('timit')
    for f in base_filenames:
        wavpath = f + '.wav'
        p = sc.predict_file(wavpath, norm_amp = False,
                        alg = 'bayes',use_segments=False)
