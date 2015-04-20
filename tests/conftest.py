
import pytest
import os

from acousticsim.utils import concatenate_files
from acousticsim.representations.base import Representation

@pytest.fixture(scope='session')
def do_long_tests():
    if os.environ.get('TRAVIS'):
        return True
    return False

@pytest.fixture(scope = 'module')
def test_dir():
    return os.path.abspath('tests/data')

@pytest.fixture(scope = 'module')
def soundfiles_dir(test_dir):
    return os.path.join(test_dir, 'soundfiles')

@pytest.fixture(scope='module')
def call_back():
    def function(*args):
        if isinstance(args[0],str):
            print(args[0])
    return function

@pytest.fixture(scope='module')
def concatenated(soundfiles_dir):
    files = [os.path.join(soundfiles_dir,x)
                for x in os.listdir(soundfiles_dir)
                if x.endswith('.wav') and '44.1k' not in x]
    return concatenate_files(files)

@pytest.fixture(scope='module')
def base_filenames(soundfiles_dir):
    filenames = [os.path.join(soundfiles_dir,os.path.splitext(x)[0])
                    for x in os.listdir(soundfiles_dir)
                    if x.endswith('.wav')]
    return filenames

@pytest.fixture(scope='module')
def praatpath():
    if os.environ.get('TRAVIS'):
        return 'praat'
    return r'C:\Users\michael\Documents\Praat\praatcon.exe'


@pytest.fixture(scope='module')
def reps_for_distance():
    source = Representation(None,None,None)
    source.rep = {1:[2,3,4],
                        2:[5,6,7],
                        3:[2,7,6],
                        4:[1,5,6]}
    target = Representation(None,None,None)
    target.rep = {1:[5,6,7],
                        2:[2,3,4],
                        3:[6,8,3],
                        4:[2,7,9],
                        5:[1,5,8],
                        6:[7,4,9]}
    return source, target
