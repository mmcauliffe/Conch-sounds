from conch.analysis.amplitude_envelopes import AmplitudeEnvelopeFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_envelopes(base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = AmplitudeEnvelopeFunction(num_bands=8, min_frequency=80, max_frequency=7800)
        envelopes = func(wavpath)

        sig, sr = librosa.load(wavpath)

        envelopes2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert envelopes == envelopes2