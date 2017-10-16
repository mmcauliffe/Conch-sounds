

class Segment(object):
    def __init__(self, **kwargs):
        self.properties = kwargs

    def __repr__(self):
        return '<Segment object with properties: {}>'.format(str(self))

    def __str__(self):
        return str(self.properties)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self.properties[item]
        elif isinstance(item, slice):
            if item.start is None:
                start = 0
            else:
                start = item.start
            if item.stop is None:
                stop = -1
            else:
                stop = item.stop
            if item.step is None:
                step = 1
            else:
                step = item.step
            return [self[i] for i in range(start, stop, step)]
        if item == 0:
            return self.properties['file_path']
        elif item == 1:
            return self.properties['begin']
        elif item == 2:
            return self.properties['end']
        elif item == 3:
            return self.properties['channel']

    def __hash__(self):
        return hash((self[0], self[1], self[2], self[3]))

    def __eq__(self, other):
        if self[0] != other[0]:
            return False
        if self[1] != other[1]:
            return False
        if self[2] != other[2]:
            return False
        if self[3] != other[3]:
            return False
        return True

    def __lt__(self, other):
        if self[0] < other[0]:
            return True
        elif self[0] == other[0]:
            if self[1] < other[1]:
                return True
            elif self[1] == other[1]:
                if self[2] < other[2]:
                    return True
        return False


class SegmentMapping(object):
    def __init__(self):
        self.segments = []

    def __len__(self):
        return len(self.segments)

    def add_segment(self, **kwargs):
        self.segments.append(Segment(**kwargs))

    def levels(self, property_key):
        return set(x[property_key] for x in self.segments)

    def grouped_mapping(self, property_key):
        data = {x: [] for x in self.levels(property_key)}
        for s in self.segments:
            data[s[property_key]].append(s)
        return data

    def __iter__(self):
        for s in self.segments:
            yield s

