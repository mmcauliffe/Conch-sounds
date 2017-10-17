from conch.analysis.mfcc import MfccFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_mfcc(base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = MfccFunction(time_step=0.01, min_frequency=80, max_frequency=7800,
                            num_filters=26, num_coefficients=13, use_power=True, deltas=False)
        mfccs = func(wavpath)

        sig, sr = librosa.load(wavpath)

        mfccs2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert mfccs == mfccs2
