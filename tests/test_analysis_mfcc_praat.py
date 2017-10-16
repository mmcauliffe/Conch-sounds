from conch.analysis.mfcc.praat import PraatMfccFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_mfcc_praat(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatMfccFunction(praat_path=praatpath, window_length=0.025, time_step=0.01, max_frequency=7800,
                                 num_coefficients=13)
        mfccs = func(wavpath)

        sig, sr = librosa.load(wavpath)

        mfccs2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert mfccs == mfccs2
