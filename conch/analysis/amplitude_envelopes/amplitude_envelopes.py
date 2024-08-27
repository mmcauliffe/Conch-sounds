import numpy as np

from scipy.signal import filtfilt, butter, hilbert
from scipy.signal import resample

from ..helper import preemphasize
from ..functions import BaseAnalysisFunction


def window_envelopes(env, win_len, time_step):
    if env.is_windowed:
        return
    nperseg = int(win_len * env.sampling_rate)
    if nperseg % 2 != 0:
        nperseg -= 1
    nperstep = int(time_step * env.sampling_rate)
    window = np.hanning(nperseg + 2)[1:nperseg + 1]
    halfperseg = int(nperseg / 2)

    print(nperseg, halfperseg)
    num_samps, num_bands = env.shape
    print(env.shape)
    indices = np.arange(halfperseg, num_samps - halfperseg + 1, nperstep)
    num_frames = len(indices)
    print(indices)
    rep = np.zeros((num_frames, num_bands))
    new_rep = dict()
    for i in range(num_frames):
        print(indices[i])
        time_key = indices[i] / env.sampling_rate
        rep_line = list()
        print(indices[i] - halfperseg, indices[i] + halfperseg)
        array = env[indices[i] - halfperseg, indices[i] + halfperseg]
        print(array.shape)
        for b in range(num_bands):
            rep_line.append(sum(array[:, b]))
        new_rep[time_key] = rep_line
    env._rep = new_rep
    env.is_windowed = True
    return env


class AmplitudeEnvelopeFunction(BaseAnalysisFunction):
    def __init__(self, num_bands=8, min_frequency=80, max_frequency=7800, mode='downsample'):
        super(AmplitudeEnvelopeFunction, self).__init__()
        self.arguments = [num_bands, min_frequency, max_frequency, mode]
        self._function = generate_amplitude_envelopes


def generate_amplitude_envelopes(signal, sr, num_bands, min_frequency, max_frequency, mode='downsample'):
    signal = preemphasize(signal, 0.97)
    proc = signal / np.sqrt(np.mean(signal ** 2)) * 0.03

    band_mins = [min_frequency * np.exp(np.log(max_frequency / min_frequency) / num_bands) ** x
                 for x in range(num_bands)]
    band_maxes = [min_frequency * np.exp(np.log(max_frequency / min_frequency) / num_bands) ** (x + 1)
                  for x in range(num_bands)]

    envs = []
    for i in range(num_bands):
        b, a = butter(2, (band_mins[i] / (sr / 2), band_maxes[i] / (sr / 2)), btype='bandpass')
        env = filtfilt(b, a, proc)
        env = np.abs(hilbert(env))
        if mode == 'downsample':
            env = resample(
                env, int(env.shape[0] * 120 / sr)
            )
        envs.append(env)
    envs = np.array(envs).T
    if mode == 'downsample':
        sr = 120
    output = dict()
    for i in range(envs.shape[0]):
        output[i / sr] = envs[i, :]
    return output
