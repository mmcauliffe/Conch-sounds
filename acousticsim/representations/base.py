
import numpy as np

from acousticsim.processing.segmentation import to_segments


class Representation(object):
    def __init__(self, file_path, data=None, attributes=None):
        self.duration = None
        self.sr = None
        self.label = None
        self.segments = None
        self.vowels = {}
        self.transcription = []
        if data is None:
            data = {}
        self.data = data
        if attributes is None:
            attributes = dict()
        self.file_path = file_path
        self.attributes = attributes
        self.is_windowed = False

    def __getitem__(self, key):
        if isinstance(key, str):
            if key in self.attributes:
                return self.attributes[key]
            else:
                return getattr(self, key, None)
        elif self.data is not None:
            if isinstance(key, tuple):
                return self.get_values_between_times(*key)
            else:
                return self.get_value_at_time(key)
        raise KeyError

    def get_values_between_times(self, begin, end):
        output = list()
        times = sorted(self.data.keys())
        for t in times:
            if t < begin:
                continue
            if t > end:
                break
            output.append(self.data[t])
        return np.array(output, dtype = np.float32)

    def get_value_at_time(self, time):
        if time in self.data:
            return self.data[time]
        times = sorted(self.data.keys())
        for i, k in enumerate(times):
            if time < k:
                end_ind = i
                break
        else:
            return None
        if end_ind == 0:
            return None
        begin_ind = end_ind - 1
        begin_time = times[begin_ind]
        end_time = times[end_ind]
        begin_val = self[begin_time]
        end_val = self[end_time]
        if begin_val is None:
            return None
        if end_val is None:
            return None
        percent = (time - begin_time) / (end_time - begin_time)
        if isinstance(begin_val,list):
            return_val = list()
            for i in range(len(begin_val)):
                if isinstance(begin_val[i],tuple):
                    v = (begin_val[i][0] * (1 - percent)) + (end_val[i][0] * percent)
                    return_val.append(v)
                else:
                    return_val.append((begin_val[i] * (1 - percent)) + (end_val[i] * percent))
            return return_val

        else:
            return (begin_val * (1 - percent)) + (end_val * percent)

    def to_array(self):
        times = sorted(self.data.keys())
        ex = next(iter(self.data.values()))
        try:
            frame_len = len(ex)
        except ValueError:
            frame_len = 1

        output = np.zeros((len(times), frame_len))
        for i, t in enumerate(times):
            output[i, :] = self.data[t]
        return output

    def window(self, win_len, time_step):
        if self.is_windowed:
            return False
        pass

    def time_from_index(self, index):
        if index >= len(self):
            return self.duration
        return sorted(self.data.keys())[index]

    def segment(self, threshold=0.1):
        if not self.is_windowed:
            return False
        segments, means = to_segments(self.to_array(), threshold=threshold, return_means=True)
        begin = 0
        self.segments = {}
        for i, end_frame in enumerate(segments):
            end_time = self.time_from_index(end_frame)
            self.segments[begin, end_time] = means[i]
            begin = end_time
        return True

    @property
    def rep(self):
        output = []
        for k in sorted(self.data.keys()):
            output.append(self.data[k])
        return np.array(output, dtype=np.float32)

    def items(self):
        for k in sorted(self.data.keys()):
            yield (k, self.data[k])

    def keys(self):
        for k in sorted(self.data.keys()):
            yield k

    def values(self):
        for k in sorted(self.data.keys()):
            yield self.data[k]

    def first(self):
        k = sorted(self.data.keys())[0]
        return self.data[k]

    def __len__(self):
        return len(self.data.keys())

    def __iter__(self):
        for k in sorted(self.data.keys()):
            yield self.data[k]

    @property
    def times(self):
        return sorted(self.data.keys())

    @property
    def vowel_durations(self):
        return [x[1] - x[0] for x in sorted(self.vowels.keys())]

    @property
    def shape(self):
        num_frames = len(self.data.keys())
        if num_frames == 0:
            return 0, 0
        else:
            return num_frames, len(next(iter(self.data.values())))
