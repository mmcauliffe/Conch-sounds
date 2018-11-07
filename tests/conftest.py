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
def autovot_filenames(autovot_dir):
    filenames = [os.path.join(autovot_dir, x)
                 for x in os.listdir(autovot_dir)
                 if x.endswith('.wav')]
    return filenames

@pytest.fixture(scope='session')
def autovot_markings(test_dir, autovot_dir):
    vot_markings = {}
    with open(os.path.join(test_dir, "vot_marks"), "r") as f:
        for x in f:
            k = os.path.join(autovot_dir, x.split(' ')[0])
            l = x.split(' ')[1:]
            v = []
            while l:
                v.append((float(l.pop(0)), float(l.pop(0))))
            vot_markings[k] = v
    return vot_markings

@pytest.fixture(scope='session')
def autovot_correct_times():
    return [(0.82, 0.005, 42.0803), (0.92, 0.005, 50.5166), (0.8, 0.005, 125.03), (0.76, 0.007, 93.6872), (0.756, 0.01, 101.213), (0.78, 0.009, 108.41), (0.774, 0.005, -62.3751), (0.807, 0.016, 85.4072), (0.64, 0.008, 70.7911), (0.753, 0.005, 63.7703), (0.692, 0.005, 103.689), (0.919, 0.021, 55.0379), (0.554, 0.005, -58.1071), (0.699, 0.024, 73.1509), (0.65, 0.011, 84.4646), (0.713, 0.022, 78.342), (0.66, 0.005, 50.3185), (0.67, 0.005, 67.515), (0.73, 0.005, 76.6631), (0.973, 0.005, -62.2706), (0.88, 0.009, 89.3114), (1.044, 0.005, 108.472), (0.704, 0.005, 93.9944), (0.93, 0.005, 65.8704), (0.73, 0.005, 111.866), (0.861, 0.005, 94.9302)]

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
