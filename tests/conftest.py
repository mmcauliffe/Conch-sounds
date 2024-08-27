import pytest
import os
import sys

from conch.utils import concatenate_files

from conch.analysis.formants import FormantTrackFunction
from conch.analysis.pitch.autocorrelation import PitchTrackFunction

from functools import partial


def pytest_addoption(parser):
    parser.addoption("--runslow", action="store_true",
                     help="run slow tests")


@pytest.fixture(scope='session')
def do_long_tests():
    if os.environ.get('TRAVIS'):
        return True
    return False


@pytest.fixture(scope='session')
def test_dir():
    base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, 'data')  # was tests/data


@pytest.fixture(scope='session')
def praat_script_test_dir(test_dir):
    return os.path.join(test_dir, 'praat_scripts')


@pytest.fixture(scope='session')
def soundfiles_dir(test_dir):
    return os.path.join(test_dir, 'soundfiles')

@pytest.fixture(scope='session')
def autovot_dir(test_dir):
    return os.path.join(test_dir, 'autovot')

@pytest.fixture(scope='session')
def tts_dir(test_dir):
    return os.path.join(test_dir, 'tts_voices')


@pytest.fixture(scope='session')
def axb_mapping_path(test_dir):
    return os.path.join(test_dir, 'axb_mapping.txt')


@pytest.fixture(scope='session')
def noise_path(soundfiles_dir):
    return os.path.join(soundfiles_dir, 'pink_noise_16k.wav')


@pytest.fixture(scope='session')
def y_path(soundfiles_dir):
    return os.path.join(soundfiles_dir, 'vowel_y_16k.wav')


@pytest.fixture(scope='session')
def acoustic_corpus_path(soundfiles_dir):
    return os.path.join(soundfiles_dir, 'acoustic_corpus.wav')

@pytest.fixture(scope='session')
def call_back():
    def function(*args):
        if isinstance(args[0], str):
            print(args[0])

    return function


@pytest.fixture(scope='session')
def concatenated(soundfiles_dir):
    files = [os.path.join(soundfiles_dir, x)
             for x in os.listdir(soundfiles_dir)
             if x.endswith('.wav') and '44.1k' not in x]
    return concatenate_files(files)


@pytest.fixture(scope='session')
def base_filenames(soundfiles_dir):
    filenames = [os.path.join(soundfiles_dir, os.path.splitext(x)[0])
                 for x in os.listdir(soundfiles_dir)
                 if x.endswith('.wav')]
    return filenames

@pytest.fixture(scope='session')
def autovot_markings(test_dir):
    vot_markings = []
    with open(os.path.join(test_dir, "vot_marks"), "r") as f:
        for x in f:
            vots = x.split(' ')
            vot_markings.append((float(vots[0]), float(vots[1])))
    return vot_markings

@pytest.fixture(scope='session')
def classifier_path(test_dir):
    return os.path.join(test_dir, "vot_model", "sotc_voiceless.classifier")

@pytest.fixture(scope='session')
def autovot_correct_times():
     return [(1.593, 0.056, 180.344), (1.828, 0.008, 126.073), (1.909, 0.071, 90.8671), (2.041, 0.005, 45.6481), (2.687, 0.016, 212.67), (2.859, 0.005, 22.646), (2.951, 0.005, 78.2495), (3.351, 0.052, 84.7406), (5.574, 0.02, 96.0191), (6.212, 0.01, 72.1773), (6.736, 0.02, 114.721), (7.02, 0.029, 224.901), (9.255, 0.032, 123.367), (9.498, 0.017, 92.7151), (11.424, 0.056, 85.1062), (13.144, 0.012, 191.111), (13.55, 0.012, 59.8446), (25.125, 0.014, 165.632)]

@pytest.fixture(scope='session')
def praatpath():
    if os.environ.get('GITHUB_ACTIONS'):
        return os.path.join(os.environ.get('HOME'), 'tools', 'praat')
    return 'praat'


@pytest.fixture(scope='session')
def reaperpath():
    return 'reaper'


@pytest.fixture(scope='session')
def reaper_func(reaperpath):
    from conch.analysis.pitch.reaper import ReaperPitchTrackFunction
    return ReaperPitchTrackFunction()


@pytest.fixture(scope='session')
def formants_func():
    func = FormantTrackFunction(max_frequency=5000, time_step=0.01, num_formants=5,
                                window_length=0.025)
    return func

@pytest.fixture(scope='session')
def pitch_func():
    func = PitchTrackFunction(min_pitch=50, max_pitch=500, time_step=0.01)
    return func


@pytest.fixture(scope='session')
def reps_for_distance():
    source = {1: [2, 3, 4],
              2: [5, 6, 7],
              3: [2, 7, 6],
              4: [1, 5, 6]}
    target = {1: [5, 6, 7],
              2: [2, 3, 4],
              3: [6, 8, 3],
              4: [2, 7, 9],
              5: [1, 5, 8],
              6: [7, 4, 9]}
    return source, target
