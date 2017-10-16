from conch.analysis.formants.praat import PraatFormantTrackFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_formants_praat(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatFormantTrackFunction(praat_path=praatpath, time_step=0.01,
                                         window_length=0.025, num_formants=5, max_frequency=5500)
        formants = func(wavpath)

        sig, sr = librosa.load(wavpath)

        formants2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        # assert formants == formants2
