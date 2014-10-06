

class Representation(object):
    _duration = None
    _sr = None
    _filepath = None
    _rep = None

    def window(self, win_len, time_step):
        pass

    def segment(self,thresh):
        pass

    @property
    def shape(self):
        return _rep.shape
