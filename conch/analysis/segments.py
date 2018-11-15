from decimal import Decimal
from itertools import product

class FileSegment(object):
    def __init__(self, file_path, begin, end, channel=0, **kwargs):
        self.file_path = file_path
        self.begin = float(Decimal(str(begin)).quantize(Decimal('0.001')))
        self.end = float(Decimal(str(end)).quantize(Decimal('0.001')))
        self.channel = channel
        self.properties = kwargs
        if 'padding' in self.properties:
            self.properties['padding'] = float(Decimal(str(self.properties['padding'])).quantize(Decimal('0.001')))

    def __repr__(self):
        return '<FileSegment object with properties: {}>'.format(str(self))

    def __str__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        if item == 'file_path':
            return self.file_path
        elif item == 'begin':
            return self.begin
        elif item == 'end':
            return self.end
        elif item == 'channel':
            return self.channel
        if item in self.properties:
            return self.properties[item]
        return None

    def __hash__(self):
        return hash((self.file_path, self.begin, self.end, self.channel))

    def __eq__(self, other):
        if not isinstance(other, FileSegment):
            return False
        if self.file_path != other.file_path:
            return False
        if self.begin != other.begin:
            return False
        if self.end != other.end:
            return False
        if self.channel != other.channel:
            return False
        if self.properties != other.properties:
            return False
        return True

    def __lt__(self, other):
        if not isinstance(other, FileSegment):
            return False
        if self.file_path < other.file_path:
            return True
        elif self.file_path == other.file_path:
            if self.begin < other.begin:
                return True
            elif self.begin == other.begin:
                if self.end < other.end:
                    return True
        return False


class SignalSegment(object):
    def __init__(self, signal, sr, **kwargs):
        self.signal = signal
        self.sr = sr
        self.properties = kwargs

    def __repr__(self):
        return '<SignalSegment object with properties: {}>'.format(str(self))

    def __str__(self):
        return str(self.__dict__)

    def __getitem__(self, item):
        if item == 'signal':
            return self.signal
        elif item == 'sr':
            return self.sr
        if item in self.properties:
            return self.properties[item]
        return None

    def __hash__(self):
        return hash((self.signal, self.sr))

    def __eq__(self, other):
        if not isinstance(other, SignalSegment):
            return False
        if self.signal != other.signal:
            return False
        if self.sr != other.sr:
            return False
        return True

    def __lt__(self, other):
        if not isinstance(other, SignalSegment):
            return False
        if self.signal < other.signal:
            return True
        elif self.signal == other.signal:
            if self.sr < other.sr:
                return True
        return False


class SegmentMapping(object):
    def __init__(self):
        self.segments = []

    def __getitem__(self, item):
        return self.segments[item]

    def __len__(self):
        return len(self.segments)

    def add_file_segment(self, file_path, begin, end, channel, **kwargs):
        self.segments.append(FileSegment(file_path, begin, end, channel, **kwargs))

    def add_signal_segment(self, signal, sr, **kwargs):
        self.segments.append(FileSegment(signal, sr, **kwargs))

    def levels(self, property_key):
        return set(x[property_key] for x in self.segments)

    def grouped_mapping(self, *properties):
        data = {x: [] for x in product(*[self.levels(y) for y in properties])}
        for s in self.segments:
            key = tuple(s[x] for x in properties)
            data[key].append(s)
        return data

    def __iter__(self):
        for s in self.segments:
            yield s

