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
def praatpath():
    if os.environ.get('TRAVIS'):
        return os.path.join(os.environ.get('HOME'), 'tools', 'praat')
    return 'praat'


@pytest.fixture(scope='session')
def reaperpath():
    if os.environ.get('TRAVIS'):
        return os.path.join(os.environ.get('HOME'), 'tools', 'reaper')
    return 'reaper'


@pytest.fixture(scope='session')
def reaper_func(reaperpath):
    from conch.analysis.pitch.reaper import ReaperPitchTrackFunction
    return ReaperPitchTrackFunction(reaper_path=reaperpath)


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
