import numpy as np
import librosa

from scipy.signal import filtfilt,butter,hilbert

from librosa import resample

from ..helper import preemphasize


def window_envelopes(env, win_len, time_step):
    if env.is_windowed:
        return
    nperseg = int(win_len * env.sampling_rate)
    if nperseg % 2 != 0:
        nperseg -= 1
    nperstep = int(time_step * env.sampling_rate)
    window = np.hanning(nperseg+2)[1:nperseg+1]
    halfperseg = int(nperseg/2)

    print(nperseg, halfperseg)
    num_samps, num_bands = env.shape
    print(env.shape)
    indices = np.arange(halfperseg, num_samps - halfperseg + 1, nperstep)
    num_frames = len(indices)
    print(indices)
    rep = np.zeros((num_frames,num_bands))
    new_rep = dict()
    for i in range(num_frames):
        print(indices[i])
        time_key = indices[i]/env.sampling_rate
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


def signal_to_amplitude_envelopes(signal, sr, num_bands, min_freq, max_freq, mode='downsample'):
    signal = preemphasize(signal, 0.97)
    proc = signal / np.sqrt(np.mean(signal ** 2)) * 0.03

    bandLo = [min_freq * np.exp(np.log(max_freq / min_freq) / num_bands) ** x
              for x in range(num_bands)]
    bandHi = [min_freq * np.exp(np.log(max_freq / min_freq) / num_bands) ** (x + 1)
              for x in range(num_bands)]

    envs = []
    for i in range(num_bands):
        b, a = butter(2, (bandLo[i] / (sr / 2), bandHi[i] / (sr / 2)), btype='bandpass')
        env = filtfilt(b, a, proc)
        env = abs(hilbert(env))
        if mode == 'downsample':
            env = resample(env, sr, 120)
        envs.append(env)
    envs = np.array(envs).T
    if mode == 'downsample':
        sr = 120
    output = dict()
    for i in range(envs.shape[0]):
        output[i / sr] = envs[i, :]
    return output


def file_to_amplitude_envelopes(file_path, num_bands, min_freq, max_freq, mode='downsample'):
    signal, sr = librosa.load(file_path, sr=None, mono=False)

    output = signal_to_amplitude_envelopes(signal, sr, num_bands, min_freq, max_freq, mode)
    return output
