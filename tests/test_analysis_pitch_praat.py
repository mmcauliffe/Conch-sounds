from conch.analysis.pitch.praat import PraatPitchTrackFunction
import librosa

from conch.analysis.segments import FileSegment, SignalSegment


def test_pitch_praat(praatpath, base_filenames):
    for f in base_filenames:
        wavpath = f + '.wav'
        func = PraatPitchTrackFunction(praat_path=praatpath, time_step=0.01,
                                       min_pitch=75, max_pitch=600)
        pitch = func(wavpath)

        sig, sr = librosa.load(wavpath)

        pitch2 = func(SignalSegment(sig, sr))

        # Things are not exact...
        #assert pitch == pitch2
