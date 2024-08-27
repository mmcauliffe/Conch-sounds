import wave
import numpy as np
from scipy.io import wavfile

from .analysis.helper import preproc


def write_wav(signal, sr, filepath):
    signal *= 32768
    wavfile.write(filepath, sr, signal.astype('int16'))


def extract_audio(filepath, outpath, begin, end, padding=0.1):
    begin -= padding
    if begin < 0:
        begin = 0
    end += padding
    with wave.open(filepath, 'rb') as inf, wave.open(outpath, 'wb') as outf:
        params = inf.getparams()
        sample_rate = inf.getframerate()
        duration = inf.getnframes() / sample_rate
        if end > duration:
            end = duration
        outf.setparams(params)
        outf.setnframes(0)
        begin_sample = int(begin * sample_rate)
        end_sample = int(end * sample_rate)
        inf.readframes(begin_sample)
        data = inf.readframes(end_sample - begin_sample)
        outf.writeframes(data)


def concatenate_files(files):
    sr = 16000
    out = np.array([])
    for f in files:
        csr, proc = preproc(f)
        # print(csr)
        # if sr != csr:
        #    raise(AcousticSimError('Files for concatenation must have the same sampling rates.'))
        out = np.append(out, proc)
    return out


def get_conch_version() -> str:
    """
    Get the current conch version

    Returns
    -------
    str
        Conch version
    """
    try:
        from ._version import version as __version__  # noqa
    except ImportError:
        __version__ = "1.0.0"
    return __version__
