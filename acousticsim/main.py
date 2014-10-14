import os
from multiprocessing import Process, Manager, Queue
import time
from queue import Empty
from collections import OrderedDict

from numpy import zeros

from functools import partial

from acousticsim.representations import Envelopes, Mfcc

from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

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
    if win_len is not None:
        use_window = True
    else:
        use_window = False
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

def acoustic_similarity_mapping(path_mapping, **kwargs):
    """Takes in an explicit mapping of full paths to .wav files to have
    acoustic similarity computed.

    Parameters
    ----------
    path_mapping : iterable of iterables
        Explicit mapping of full paths of .wav files, in the form of a
        list of tuples to be compared.
    rep : {'envelopes','mfcc'}, optional
        The type of representation to convert the wav files into before
        comparing for similarity.  Amplitude envelopes will be computed
        when 'envelopes' is specified, and MFCCs will be computed when
        'mfcc' is specified (default).
    match_function : {'dtw', 'xcorr'}, optional
        How similarity/distance will be calculated.  Defaults to 'dtw' to
        use Dynamic Time Warping (can be slower) to compute distance.
        Cross-correlation can be specified with 'xcorr', which computes
        distance as the inverse of a maximum cross-correlation value
        between 0 and 1.
    num_filters : int, optional
        The number of frequency filters to use when computing representations.
        Defaults to 8 for amplitude envelopes and 26 for MFCCs.
    num_coeffs : int, optional
        The number of coefficients to use for MFCCs (not used for
        amplitude envelopes).  Default is 20, which captures speaker-
        specific information, whereas 12 would be more speaker-independent.
    freq_lims : tuple, optional
        A tuple of the minimum frequency and maximum frequency in Hertz to use
        for computing representations.  Defaults to (80, 7800) following
        Lewandowski's dissertation (2012).
    output_sim : bool, optional
        If true (default), the function will return similarities (inverse distance).
        If false, distance measures will be returned instead.
    verbose : bool, optional
        If true, command line progress will be displayed after every 50
        mappings have been processed.  Defaults to false.

    Returns
    -------
    list of tuples
        Returns a list of tuples corresponding to the `path_mapping` input,
        with a new final element in the tuple being the similarity/distance
        score for that mapping.

    """

    to_rep = _build_to_rep(**kwargs)

    num_cores = kwargs.get('num_cores', 1)
    attributes = kwargs.get('attributes',dict())

    match_function = kwargs.get('match_function', 'dtw')
    cache = kwargs.get('cache',None)
    if match_function == 'xcorr':
        dist_func = xcorr_distance
    elif match_function == 'dct':
        dist_func = dct_distance
    else:
        dist_func = dtw_distance
    if cache is None:
        cache = generate_cache(path_mapping, to_rep, num_cores, attributes)
    asim = calc_asim(path_mapping,cache,dist_func,num_cores)

    if kwargs.get('return_rep',False):
        return asim, cache

    return asim



def acoustic_similarity_directories(directory_one,directory_two, **kwargs):
    """Computes acoustic similarity across two directories of .wav files.

    Parameters
    ----------
    directory_one : str
        Full path of the first directory to be compared.
    directory_two : str
        Full path of the second directory to be compared.
    all_to_all : bool, optional
        If true (default), do all possible comparisons between the two
        directories.  If false, try to do pairwise comparisons between
        files.
    rep : {'envelopes','mfcc'}, optional
        The type of representation to convert the wav files into before
        comparing for similarity.  Amplitude envelopes will be computed
        when 'envelopes' is specified, and MFCCs will be computed when
        'mfcc' is specified.
    match_function : {'dtw', 'xcorr'}, optional
        How similarity/distance will be calculated.  Defaults to 'dtw' to
        use Dynamic Time Warping (can be slower) to compute distance.
        Cross-correlation can be specified with 'xcorr', which computes
        distance as the inverse of a maximum cross-correlation value
        between 0 and 1.
    num_filters : int, optional
        The number of frequency filters to use when computing representations.
        Defaults to 8 for amplitude envelopes and 26 for MFCCs.
    num_coeffs : int, optional
        The number of coefficients to use for MFCCs (not used for
        amplitude envelopes).  Default is 20, which captures speaker-
        specific information, whereas 12 would be more speaker-independent.
    freq_lims : tuple, optional
        A tuple of the minimum frequency and maximum frequency in Hertz to use
        for computing representations.  Defaults to (80, 7800) following
        Lewandowski's dissertation (2012).
    output_sim : bool, optional
        If true (default), the function will return similarities (inverse distance).
        If false, distance measures will be returned instead.
    verbose : bool, optional
        If true, command line progress will be displayed after every 50
        mappings have been processed.  Defaults to false.

    Returns
    -------
    float
        Average distance/similarity of all the comparisons that were done
        between the two directories.

    """

    files_one = os.listdir(directory_one)
    files_two = os.listdir(directory_two)

    path_mapping = [ (os.path.join(directory_one,x),
                        os.path.join(directory_two,y))
                        for x in files_one
                        for y in files_two]
    output = acoustic_similarity_mapping(path_mapping, **kwargs)
    output_val = sum([x for x in output.values()]) / len(output.values())

    threaded_q = kwargs.get('threaded_q', None)
    if not threaded_q:
        return output_val
    else:
        threaded_q.put(output_val)
        return None

def analyze_directories(directories, **kwargs):

    files = []
    kwargs['attributes'] = dict()
    for d in directories:
        if not os.path.isdir(d):
            continue

        files += [os.path.join(d,x) for x in os.listdir(d) if x.lower().endswith('.wav')]

        att_path = os.path.join(d,'attributes.txt')
        if os.path.exists(att_path):
            kwargs['attributes'].update(load_attributes(att_path))


    path_mapping = [ (x,y)
                        for x in files
                        for y in files if x != y]
    result = acoustic_similarity_mapping(path_mapping, **kwargs)
    return result

def analyze_directory(directory, **kwargs):
    kwargs['attributes'] = dict()
    all_files = [os.path.join(directory,x) for x in os.listdir(directory)]
    wavs = list(filter(lambda x: x.lower().endswith('.wav'),all_files))
    if not wavs:
        directories = list(filter(lambda x: os.path.isdir(x),all_files))
        return analyze_directories(directories, **kwargs)

    att_path = os.path.join(directory,'attributes.txt')
    if os.path.exists(att_path):
        kwargs['attributes'].update(load_attributes(att_path))

    path_mapping = [ (x,y)
                        for x in wavs
                        for y in wavs if x != y]
    result = acoustic_similarity_mapping(path_mapping, **kwargs)
    return result

def analyze_single_file(path, output_path,**kwargs):
    from acousticsim.representations.helper import extract_wav
    to_rep = _build_to_rep(**kwargs)

    time_step = kwargs.get('time_step', 0.01)
    rep = to_rep(path)
    print('Created MFCCs')
    #raise(ValueError)
    segs = to_segments(rep,debug=True)
    #print(segs)
    #print([x*time_step for x in segs])
    begin = 0
    for i, s in enumerate(segs):
        begin_time = begin * time_step
        end_time = (s+1) * time_step
        extract_wav(path,os.path.join(output_path,'%d.wav'%i),begin_time,end_time)
        begin = s+1


if __name__ == '__main__':
    kwarg_dict = {'rep': 'mfcc','freq_lims':(80,7800),'num_coeffs': 20,
                    'num_filters': 26, 'win_len': 0.025, 'time_step': 0.01,
                    'use_power': True}
    analyze_single_file(r"C:\Users\michael\Documents\Data\VIC\Processed\s0101a.wav",
                        r'C:\Users\michael\Documents\Data\Segs',**kwarg_dict)

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

def rep_worker(job_q,return_dict,rep_func,attributes):
    while True:
        try:
            filename = job_q.get(timeout=1)
        except Empty:
            break
        path, filelabel = os.path.split(filename)
        att = OrderedDict()
        att['filename'] = filelabel
        try:
            att.update(attributes[filelabel])
        except KeyError:
            pass
        true_label = os.path.split(path)[1]
        rep = rep_func(filename,attributes=att)
        rep._true_label = true_label
        return_dict[os.path.split(filename)[1]] = rep

def generate_cache(path_mapping,rep_func,num_procs, attributes):
    all_files = set()
    for pm in path_mapping:
        all_files.update(pm)

    job_queue = Queue()

    for f in all_files:
        job_queue.put(f)

    manager = Manager()
    return_dict = manager.dict()
    procs = []
    for i in range(num_procs):
        p = Process(
                target=rep_worker,
                args=(job_queue,
                      return_dict,rep_func,attributes))
        procs.append(p)
        p.start()
    time.sleep(10)
    for p in procs:
        p.join()

    return return_dict

def dist_worker(job_q,return_dict,dist_func,axb,cache):
    while True:
        try:
            pm = job_q.get(timeout=1)
        except Empty:
            break
        filetup = tuple(map(lambda x: os.path.split(x)[1],pm))
        base = cache[filetup[0]]
        model = cache[filetup[1]]
        dist1 = dist_func(base,model)
        if axb:
            shadow = cache[filetup[2]]
            dist2 = dist_func(shadow,model)
            ratio = dist2 / dist1
        else:
            ratio = dist1

        return_dict[filetup] = ratio

def queue_adder(path_mapping,queue):
    for pm in path_mapping:
        queue.put(pm,timeout=30)

def calc_asim(path_mapping, cache,dist_func,num_procs):
    if len(path_mapping[0]) == 3:
        axb = True
    else:
        axb = False

    job_queue = Queue()

    job_p = Process(target=queue_adder,
                    args = (path_mapping,job_queue))
    job_p.start()
    time.sleep(2)
    manager = Manager()
    return_dict = manager.dict()
    procs = []
    for i in range(num_procs):
        p = Process(
                target=dist_worker,
                args=(job_queue,
                      return_dict,dist_func,axb,cache))
        procs.append(p)
        p.start()
    time.sleep(2)
    job_p.join()
    for p in procs:
        p.join()

    return return_dict

