
import os
import pytest

from conch.io import load_path_mapping


def test_valid(test_dir):
    valid_path = os.path.join(test_dir,'mapping_test.txt')
    mapping = load_path_mapping(valid_path)
    for line in mapping:
        assert(len(line) == 2)

def test_invalid(test_dir):
    invalid_path = os.path.join(test_dir,'invalid_mapping_test.txt')
    with pytest.raises(OSError):
        mapping = load_path_mapping(invalid_path)

