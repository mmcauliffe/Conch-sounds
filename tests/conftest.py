
import pytest
import os

from acousticsim.utils import concatenate_files

@pytest.fixture(scope='module')
def test_dir():
    return os.path.abspath('tests/data')

@pytest.fixture(scope='module')
def call_back():
    def function(*args):
        if isinstance(args[0],str):
            print(args[0])
    return function

@pytest.fixture(scope='module')
def concatenated(test_dir):
    files = [os.path.join(test_dir,x)
                for x in os.listdir(test_dir)
                if x.endswith('.wav') and '44.1k' not in x]
    return concatenate_files(files)

@pytest.fixture(scope='module')
def base_filenames(test_dir):
    filenames = [os.path.join(test_dir,os.path.splitext(x)[0])
                    for x in os.listdir(test_dir)
                    if x.endswith('.wav')]
    return filenames

@pytest.fixture(scope='module')
def praatpath():
    return 'praatcon.exe'
