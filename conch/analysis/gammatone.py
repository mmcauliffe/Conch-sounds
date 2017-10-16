from numpy import pi,exp,log,abs,sum,sqrt,array, hanning, arange, zeros,cos,ceil,mean

from scipy.signal import filtfilt,butter,hilbert

from .helper import preproc,make_erb_cfs,nextpow2,fftfilt


def to_gammatone(path,num_bands,freq_lims):
    sr, proc = preproc(path,alpha=0)

    proc = proc / 32768 #hack!! for 16-bit pcm
    cfs = make_erb_cfs(freq_lims,num_bands)

    filterOrder = 4 # filter order
    gL = 2**nextpow2(0.128*sr) # gammatone filter length at least 128 ms
    b = 1.019*24.7*(4.37*cfs/1000+1) # rate of decay or bandwidth

    tpt=(2*pi)/sr
    gain=((1.019*b*tpt)**filterOrder)/6 # based on integral of impulse

    tmp_t = arange(gL)/sr

    envelopes = []
    bms = []

    # calculate impulse response
    for i in range(num_bands):
        gt = gain[i]*sr**3*tmp_t**(filterOrder-1)*exp(-2*pi*b[i]*tmp_t)*cos(2*pi*cfs[i]*tmp_t)
        bm = fftfilt(gt,proc)
        bms.append(bm)
        env = abs(hilbert(bm))
        envelopes.append(env)
    return array(bms).T,array(envelopes).T

