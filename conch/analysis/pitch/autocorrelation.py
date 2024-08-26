import librosa
from numpy import log10, arange, hanning, log, correlate, max, mean, maximum, inf
from scipy.signal.windows import gaussian
from scipy.signal import argrelmax
from ..functions import BaseAnalysisFunction


def find_best_path(candidate_matrix, num_candidates, voice_change_cost, octave_jump_cost):
    def transition_cost(f1, f2):
        if f1 == 0 and f2 == 0:
            return 0
        elif f1 == 0 or f2 == 0:
            return voice_change_cost
        else:
            return octave_jump_cost * log(f1 / f2)

    V = [{}]
    path = {}

    # Initialize base cases (t == 0)
    for y in range(num_candidates):
        try:
            V[0][y] = candidate_matrix[0][y][1]
            path[y] = [y]
        except IndexError:
            pass

    num_frames = len(candidate_matrix)
    # Run Viterbi for t > 0
    for t in range(1, num_frames):
        V.append({})
        newpath = {}
        for y in range(num_candidates):
            best = inf
            state = -1
            try:
                freq, r = candidate_matrix[t][y]
            except IndexError:
                continue
            for y0 in range(num_candidates):
                try:
                    cost = V[t - 1][y0]
                    cost += transition_cost(candidate_matrix[t - 1][y0][0],
                                            freq)
                    cost -= r
                except (IndexError, KeyError):
                    continue

                if cost < best:
                    best = cost
                    state = y0
            V[t][y] = best
            newpath[y] = path[state] + [y]

        # Don't need to remember the old paths
        path = newpath
    n = 0  # if only one element is observed max is sought in the initialization values
    if num_frames != 1:
        n = t
    best = inf
    state = -1
    for y in range(num_candidates):
        try:
            c = V[n][y]
        except KeyError:
            continue
        if c < best:
            best = c
            state = y
    return path[state]


def ac_pitch(signal, sr, time_step, min_pitch, max_pitch,
             # Praat parameters
             window_shape='gaussian',
             sil_thresh=0.03,
             voice_thresh=0.45,
             octave_cost=0.01,
             octave_jump_cost=0.35,
             voice_change_cost=0.14,
             num_candidates=15,
             periods_per_window=3):
    win_len = periods_per_window / min_pitch
    if window_shape == 'gaussian':
        win_len *= 2
    maxsignal = max(signal)
    nperseg = int(win_len * sr)
    nperstep = int(time_step * sr)
    if window_shape == 'gaussian':
        window = gaussian(nperseg + 2, 0.5 * (nperseg - 1) / 2)[1:nperseg + 2]
    else:
        window = hanning(nperseg + 2)[1:nperseg + 1]

    maxpos = int(1 / min_pitch * sr)
    minpos = int(1 / max_pitch * sr)

    indices = arange(int(nperseg / 2), signal.shape[0] - int(nperseg / 2), nperstep)
    num_frames = len(indices)
    win_ac = correlate(window, window, 'full')
    win_ac = win_ac[int(win_ac.size / 2):] / max(win_ac)

    candidate_matrix = []
    for i in range(num_frames):
        X = signal[indices[i] - int(nperseg / 2):indices[i] + int(nperseg / 2) + 1]
        try:
            X = X * window
        except ValueError:
            print(i, num_frames)
            print(indices[i], len(signal))
            raise (ValueError)
        X -= mean(X)

        unvoicedR = voice_thresh + maximum(0, 2 - (max(X) / maxsignal) / (sil_thresh / (1 + voice_thresh)))
        candidates = [(0, unvoicedR)]
        ac = correlate(X, X, 'full')

        sig_ac = ac[int(ac.size / 2):] / max(ac)

        orig_ac = sig_ac / win_ac
        cands = minpos + argrelmax(orig_ac[minpos:maxpos])[0]
        values = orig_ac[cands]
        inds = values.argsort()
        cands = cands[inds][:num_candidates]
        for pos in cands:
            f0 = 1 / (pos / sr)
            R = orig_ac[pos] - octave_cost * log(min_pitch * pos)
            candidates.append((f0, R))

        candidate_matrix.append(candidates)

    path = find_best_path(candidate_matrix, num_candidates, voice_change_cost, octave_jump_cost)
    output = {}
    for i, p in enumerate(path):
        output[indices[i] / sr] = [candidate_matrix[i][p][0]]
    return output


class PitchTrackFunction(BaseAnalysisFunction):
    def __init__(self, time_step=0.01, min_pitch=50, max_pitch=500):
        super(PitchTrackFunction, self).__init__()
        self.arguments = [time_step, min_pitch, max_pitch]
        self.requires_file = False
        self._function = ac_pitch


def ac_harmonicity(signal, sr, time_step, min_pitch, max_pitch,
                   # Praat parameters
                   window_shape='gaussian',
                   sil_thresh=0.03,
                   voice_thresh=0.45,
                   octave_cost=0.01,
                   octave_jump_cost=0.35,
                   voice_change_cost=0.14,
                   num_candidates=15,
                   periods_per_window=3):
    win_len = periods_per_window / min_pitch
    if window_shape == 'gaussian':
        win_len *= 2
    nperseg = int(win_len * sr)
    nperstep = int(time_step * sr)
    if window_shape == 'gaussian':
        window = gaussian(nperseg + 2, 0.5 * (nperseg - 1) / 2)[1:nperseg + 2]
    else:
        window = hanning(nperseg + 2)[1:nperseg + 1]

    maxpos = int(1 / min_pitch * sr)
    indices = arange(int(nperseg / 2), signal.shape[0] - int(nperseg / 2), nperstep)
    num_frames = len(indices)
    output = dict()
    win_ac = correlate(window, window, 'full')
    win_ac = win_ac[int(win_ac.size / 2):] / max(win_ac)
    for i in range(num_frames):
        X = signal[indices[i] - int(nperseg / 2):indices[i] + int(nperseg / 2) + 1]
        X = X * window
        X -= mean(X)
        ac = correlate(X, X, 'full')
        sig_ac = ac[int(ac.size / 2):] / max(ac)

        orig_ac = sig_ac / win_ac

        cands = argrelmax(orig_ac[:maxpos])[0]
        rs = orig_ac[cands]
        if len(rs) > 0:
            r = max(rs)
        else:
            r = -1
        if r > 1:
            r = 1 / r

        elif r < 0:
            r = 0.0001
            # print(argrelmax(orig_ac[:maxpos])[0])
            # print(rs)
            # plt.plot(orig_ac)
            # plt.show()
        output[indices[i] / sr] = [10 * log10(r / (1 - r))]
    return output
