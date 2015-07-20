import os
from multiprocessing import Process, Manager, Queue, cpu_count, Value, Lock, JoinableQueue
import time
from queue import Empty, Full
from collections import OrderedDict

from numpy import zeros

from functools import partial

from acousticsim.representations import Envelopes, Mfcc

from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

from acousticsim.exceptions import AcousticSimError,NoWavError
from acousticsim.multiprocessing import generate_cache, calc_asim

from textgrid import TextGrid

def _build_to_rep(**kwargs):
    rep = kwargs.get('rep', 'mfcc')


    num_filters = kwargs.get('num_filters',None)
    num_coeffs = kwargs.get('num_coeffs', 20)

    freq_lims = kwargs.get('freq_lims', (80, 7800))

    win_len = kwargs.get('win_len', None)
    time_step = kwargs.get('time_step', None)

    use_power = kwargs.get('use_power', True)

    if num_filters is None:
        if rep == 'envelopes':
            num_filters = 8
        else:
            num_filters = 26
    if win_len is None:
        win_len = 0.025
    if time_step is None:
        time_step = 0.01


    if rep == 'envelopes':
        to_rep = partial(Envelopes,
                                num_bands=num_filters,
                                freq_lims=freq_lims)
    elif rep == 'mfcc':
        to_rep = partial(Mfcc,freq_lims=freq_lims,
                                    num_coeffs=num_coeffs,
                                    num_filters = num_filters,
                                    win_len=win_len,
                                    time_step=time_step,
                                    use_power = use_power)
    elif rep in ['mhec','gammatone','melbank','formats','pitch','prosody']:
        raise(NotImplementedError)
    else:
        raise(Exception("The type of representation must be one of: 'envelopes', 'mfcc'."))
    #elif rep == 'mhec':
    #    to_rep = partial(to_mhec, freq_lims=freq_lims,
    #                                num_coeffs=num_coeffs,
    #                                num_filters = num_filters,
    #                                window_length=win_len,
    #                                time_step=time_step,
    #                                use_power = use_power)
    #elif rep == 'gammatone':
        #if use_window:
            #to_rep = partial(to_gammatone_envelopes,num_bands = num_filters,
                                                #freq_lims=freq_lims,
                                                #window_length=win_len,
                                                #time_step=time_step)
        #else:
            #to_rep = partial(to_gammatone_envelopes,num_bands = num_filters,
                                                #freq_lims=freq_lims)
    #elif rep == 'melbank':
        #to_rep = partial(to_melbank,freq_lims=freq_lims,
                                    #win_len=win_len,
                                    #time_step=time_step,
                                    #num_filters = num_filters)
    #elif rep == 'prosody':
        #to_rep = partial(to_prosody,time_step=time_step)
    return to_rep

def load_attributes(path):
    from csv import DictReader
    outdict = OrderedDict()
    with open(path,'r') as f:
        reader = DictReader(f,delimiter='\t')
        for line in reader:
            name = line['filename']
            del line['filename']
            linedict = OrderedDict()
            for k in reader.fieldnames:
                if k == 'filename':
                    continue
                try:
                    linedict[k] = float(line[k])
                except ValueError:
                    linedict[k] = line[k]
            outdict[name] = linedict
    return outdict

def get_vowel_points(textgrid_path, tier_name = 'Vowel', vowel_label = 'V'):
    tg = TextGrid()
    tg.read(textgrid_path)
    vowel_tier = tg.getFirst(tier_name)
    for i in vowel_tier:
        if i.mark == vowel_label:
            begin = i.minTime
            end = i.maxTime
            break
    else:
        raise(AcousticSimError('No vowel label was found in \'{}\'.'.format(textgrid_path)))
    return begin, end

