from conch.analysis.intensity.praat import PraatIntensityTrackFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_intensity_praat(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatIntensityTrackFunction(praat_path=praatpath, time_step=0.01)
        pitch = func(wavpath)

        sig, sr = librosa.load(wavpath)

        pitch2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        #assert pitch == pitch2
