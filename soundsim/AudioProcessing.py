'''
Created on 2012-08-15

@author: michael
'''
from pylab import *
import pyaudio
import wave
import struct

datadir = "/home/michael/dev/MentalLexicon/Data/"

def createWAV():
    freq=440.0
    data_size=40000
    fname=datadir+"test.wav"
    frate=11025.0 
    amp=64000.0   
    nchannels=1
    sampwidth=2
    framerate=int(frate)
    nframes=data_size
    comptype="NONE"
    compname="not compressed"
    data=[math.sin(2*math.pi*freq*(x/frate))
          for x in range(data_size)]
    wav_file=wave.open(fname, 'w')    
    wav_file.setparams((nchannels,sampwidth,framerate,nframes,comptype,compname))
    for v in data:
        wav_file.writeframes(struct.pack('h', int(v*amp/2)))
    wav_file.close()

def readWAV():
    data_size=40000
    fname=datadir+"test.wav"
    frate=11025.0 
    wav_file=wave.open(fname,'r')
    data=wav_file.readframes(data_size)
    wav_file.close()
    data=struct.unpack('{n}h'.format(n=data_size), data)
    print data[:30]
    data=np.array(data)

    w = np.fft.fft(data)
    print w.ndim
    freqs = np.fft.fftfreq(len(w))
    print(freqs.min(),freqs.max())
    # (-0.5, 0.499975)

    # Find the peak in the coefficients
    idx=np.argmax(np.abs(w)**2)
    freq=freqs[idx]
    freq_in_hertz=abs(freq*frate)
    print(freq_in_hertz)

if __name__ == '__main__':
    #createWAV()
    #readWAV()
    fname = datadir+"440_sine.wav"
    wf = wave.open(fname,'r')
    num_channels = wf.getnchannels()
    sample_rate = wf.getframerate()
    sample_width = wf.getsampwidth()
    num_frames = wf.getnframes()
    raw_data = wf.readframes(num_frames)
    wf.close()
    
    print num_channels
    print sample_rate
    print sample_width
    print num_frames
    total_samples = num_frames * num_channels
    if sample_width == 1:
        fmt = '%iB'%total_samples
    elif sample_width == 2:
        fmt = '%ih' %total_samples
    else:
        raise ValueError("Only supports 8 and 16 bit audio formats.")
    int_data=wave.struct.unpack(fmt, raw_data)
    del raw_data
    
    channels = [ [] for time in range(num_channels)]
    
    for index, value in enumerate(int_data):
        bucket = index % num_channels
        channels[bucket].append(value)
    
    data = np.array(channels[1])
    w = np.fft.fft(data)
    freqs = np.fft.fftfreq(len(w))
    print w.ndim
    #return channels, sample_rate