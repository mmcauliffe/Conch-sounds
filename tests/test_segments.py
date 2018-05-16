import pytest

from conch.analysis.segments import SegmentMapping

def test_grouping():
    mapping = SegmentMapping()
    speakers = ['speaker1', 'speaker2']
    vowels = ['aa', 'ae', 'iy']
    for s in speakers:
        if s == 'speaker1':
            vs = ['aa', 'ae']
        else:
            vs = ['aa', 'iy']
        for v in vs:
            mapping.add_file_segment('path', 0, 1, 0, speaker=s, vowel=v)

    groups = mapping.grouped_mapping('speaker', 'vowel')
    assert len(groups) == 6
    for g, lists in groups.items():
        assert g[0] in speakers
        assert g[1] in vowels

    groups = mapping.grouped_mapping('vowel', 'speaker')
    assert len(groups) == 6
    for g, lists in groups.items():
        assert g[0] in vowels
        assert g[1] in speakers
