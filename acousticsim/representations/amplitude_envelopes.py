from numpy import pi,exp,log,abs,sum,sqrt,array, hanning, arange, zeros,cos,ceil,mean

from scipy.signal import filtfilt,butter,hilbert,resample
from acousticsim.representations.helper import preproc,make_erb_cfs,nextpow2,fftfilt

def to_envelopes(path,num_bands,freq_lims,window_length=None,time_step=None):
    """Generate amplitude envelopes from a full path to a .wav, following
    Lewandowski (2012).

    Parameters
    ----------
    filename : str
        Full path to .wav file to process.
    freq_lims : tuple
        Minimum and maximum frequencies in Hertz to use.
    num_bands : int
        Number of frequency bands to use.
    win_len : float, optional
        Window length in seconds for using windows. By default, the
        envelopes are resampled to 120 Hz instead of windowed.
    time_step : float
        Time step in seconds for windowing. By default, the
        envelopes are resampled to 120 Hz instead of windowed.

    Returns
    -------
    2D array
        Amplitude envelopes over time.  If using windowing, the first
        dimension is the time in frames, but by default the first
        dimension is time in samples with a 120 Hz sampling rate.
        The second dimension is the amplitude envelope bands.

    """
    sr, proc = preproc(path,alpha=0.97)
    proc = proc/sqrt(mean(proc**2))*0.03;
    bandLo = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**x for x in range(num_bands)]
    bandHi = [ freq_lims[0]*exp(log(freq_lims[1]/freq_lims[0])/num_bands)**(x+1) for x in range(num_bands)]
    if window_length is not None and time_step is not None:
        use_windows = True
        nperseg = int(window_length*sr)
        noverlap = int(time_step*sr)
        window = hanning(nperseg+2)[1:nperseg+1]
        step = nperseg - noverlap
        indices = arange(0, proc.shape[-1]-nperseg+1, step)
        num_frames = len(indices)
        envelopes = zeros((num_bands,num_frames))
    else:
        use_windows=False
        sr_env = 120
        t = len(proc)/sr
        numsamp = ceil(t * sr_env)
        envelopes = []
    for i in range(num_bands):
        b, a = butter(2,(bandLo[i]/(sr/2),bandHi[i]/(sr/2)), btype = 'bandpass')
        env = filtfilt(b,a,proc)
        env = abs(hilbert(env))
        if use_windows:
            window_sums = []
            for k,ind in enumerate(indices):
                seg = env[ind:ind+nperseg] * window
                window_sums.append(sum(seg))
            envelopes[i,:] = window_sums
        else:
            env = resample(env,numsamp)
            envelopes.append(env)
    return array(envelopes).T

def to_gammatone_envelopes(path,num_bands,freq_lims,window_length=None,time_step=None):
    sr, proc = preproc(path)
    cfs = make_erb_cfs(freq_lims,num_bands)

    filterOrder = 4 # filter order
    gL = 2**nextpow2(0.128*sr) # gammatone filter length at least 128 ms
    b = 1.019*24.7*(4.37*cfs/1000+1) # rate of decay or bandwidth

    tpt=(2*pi)/sr
    gain=((1.019*b*tpt)**filterOrder)/6 # based on integral of impulse

    tmp_t = arange(gL)/sr

    if window_length is not None and time_step is not None:
        use_windows = True
        nperseg = int(window_length*sr)
        noverlap = int(time_step*sr)
        window = hanning(nperseg+2)[1:nperseg+1]
        step = nperseg - noverlap
        indices = arange(0, proc.shape[-1]-nperseg+1, step)
        num_frames = len(indices)
        envelopes = zeros((num_frames,num_bands))
    else:
        use_windows=False
        sr_env = 120
        t = len(proc)/sr
        numsamp = t * sr_env * 2
        envelopes = []

    # calculate impulse response
    for i in range(num_bands):
        gt = gain[i]*sr**3*tmp_t**(filterOrder-1)*exp(-2*pi*b[i]*tmp_t)*cos(2*pi*cfs[i]*tmp_t)
        bm = fftfilt(gt,proc)
        env = abs(hilbert(bm))
        if use_windows:
            for k,ind in enumerate(indices):
                seg = env[ind:ind+nperseg] * window
                envelopes[k,i] = sum(seg)
        else:
            env = resample(env,numsamp)
            envelopes.append(env)
    return array(envelopes).T
