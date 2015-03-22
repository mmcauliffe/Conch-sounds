
import numpy as np

from .representations.helper import preproc

from .exceptions import AcousticSimError

def concatenate_files(files):
    sr = 16000
    out = np.array([])
    for f in files:
        csr, proc = preproc(f)
        #print(csr)
        #if sr != csr:
        #    raise(AcousticSimError('Files for concatenation must have the same sampling rates.'))
        out = np.append(out,proc)
    return out
