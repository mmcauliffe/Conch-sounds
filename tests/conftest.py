
import pytest

@pytest.fixture(scope='module')
def call_back():
    def function(*args):
        if isinstance(args[0],str):
            print(args[0])
    return function
