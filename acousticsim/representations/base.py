

class Representation(object):
    _duration = None
    _sr = None
    _filepath = None
    _rep = None
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
            return self._rep[key]

    def window(self, win_len, time_step):
        pass

    def segment(self,thresh):
        pass

    @property
    def shape(self):
        return self._rep.shape
