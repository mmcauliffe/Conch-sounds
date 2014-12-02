
import numpy as np


class Representation(object):
    _duration = None
    _sr = None
    _filepath = None
    _rep = dict()
    _true_label = None
    _attributes = None

    def __init__(self,filepath, freq_lims, attributes):
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
            return self.get_value_at_time(key)
        raise(KeyError)

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
        begin_val = self._rep[begin_time]
        end_val = self._rep[end_time]
        if begin_val is None:
            return None
        if end_val is None:
            return None
        percent = (time - begin_time) / (end_time - begin_time)
        if isinstance(begin_val,list):
            return_val = list()
            for i in range(len(begin_val)):
                return_val.append((begin_val[i] * (1 - percent)) + (end_val[i] * (percent)))
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
        pass

    def segment(self,thresh):
        pass

    def rep(self):
        output = list()
        for k in sorted(self._rep.keys()):
            output.append(self._rep[k])
        return np.array(output)

    def set_rep(self, rep):
        self._rep = rep

    @property
    def shape(self):
        return self._rep.shape
