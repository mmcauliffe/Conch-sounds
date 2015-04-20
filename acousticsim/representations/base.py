
import numpy as np

from acousticsim.processing.segmentation import to_segments

class Representation(object):
    _duration = None
    _sr = None
    _filepath = None
    _rep = dict()
    _true_label = None
    _attributes = None
    _segments = None
    _is_windowed = False

    def __init__(self, filepath, freq_lims, attributes):
        self._vowels = dict()
        self._transcription = list()
        self._rep = dict()
        if attributes is None:
            attributes = dict()
        self._filepath = filepath
        self._freq_lims = freq_lims
        self._attributes = attributes


    def __getitem__(self,key):
        if isinstance(key,str):
            if key in self._attributes:
                return self._attributes[key]
            else:
                return getattr(self,key,None)
        elif self._rep is not None:
            if isinstance(key, tuple):
                return self.get_values_between_times(*key)
            else:
                return self.get_value_at_time(key)
        raise(KeyError)

    def get_values_between_times(self, begin, end):
        output = list()
        times = sorted(self._rep.keys())
        for t in times:
            if t < begin:
                continue
            if t > end:
                break
            output.append(self._rep[t])
        return output

    def get_value_at_time(self,time):
        if time in self._rep:
            return self._rep[time]
        times = sorted(self._rep.keys())
        begin_ind = 0
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
                    v = (begin_val[i][0] * (1 - percent)) + (end_val[i][0] * (percent))
                    return_val.append(v)
                else:
                    return_val.append((begin_val[i] * (1 - percent)) + (end_val[i] * (percent)))
            return return_val

        else:
            return (begin_val * (1 - percent)) + (end_val * (percent))

    def to_array(self):
        times = sorted(self._rep.keys())
        ex = next(iter(self._rep.values()))
        try:
            frame_len = len(ex)
        except:
            frame_len = 1

        output = np.zeros((len(times),frame_len))
        for i, t in enumerate(times):
            output[i,:] = self._rep[t]
        return output

    def window(self, win_len, time_step):
        if self._is_windowed:
            return False
        pass

    def time_from_index(self,index):
        if index >= len(self):
            return self._duration
        return sorted(self._rep.keys())[index]

    def segment(self,threshold = 0.1):
        if not self._is_windowed:
            return False
        segments, means = to_segments(self.to_array(), threshold = threshold,return_means=True)
        begin = 0
        self._segments = dict()
        for i,end_frame in enumerate(segments):
            end_time = self.time_from_index(end_frame)
            self._segments[begin, end_time] = means[i]
            begin = end_time
        return True

    @property
    def rep(self):
        output = list()
        for k in sorted(self._rep.keys()):
            output.append(self._rep[k])
        return np.array(output)

    @rep.setter
    def rep(self, value):
        self._rep = value

    def items(self):
        for k in sorted(self._rep.keys()):
            yield (k,self._rep[k])

    def keys(self):
        for k in sorted(self._rep.keys()):
            yield k

    def values(self):
        for k in sorted(self._rep.keys()):
            yield self._rep[k]

    def first(self):
        k = sorted(self._rep.keys())[0]
        return self._rep[k]

    def __len__(self):
        return len(self._rep.keys())

    def __iter__(self):
        for k in sorted(self._rep.keys()):
            yield self._rep[k]

    @property
    def vowel_times(self):
        return self._vowels

    @vowel_times.setter
    def vowel_times(self, times):
        self._vowels = times

    @property
    def transcription(self):
        return self._transcription

    @transcription.setter
    def transcription(self, value):
        self._transcription = value

    @property
    def times(self):
        return sorted(self._rep.keys())

    @property
    def vowel_durations(self):
        return [x[1] - x[0] for x in sorted(self._vowels.keys())]

    @property
    def shape(self):
        return self._rep.shape

    @property
    def sampling_rate(self):
        return self._sr
