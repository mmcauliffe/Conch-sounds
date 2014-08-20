import os
from multiprocessing import Process, Manager, Queue
import time
from queue import Empty

from numpy import zeros

from functools import partial

from acousticsim.representations import to_envelopes, to_mfcc, to_mhec

from acousticsim.distance import dtw_distance, xcorr_distance

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

    rep = kwargs.get('rep', 'mfcc')

    match_function = kwargs.get('match_function', 'dtw')

    num_filters = kwargs.get('num_filters',None)
    num_coeffs = kwargs.get('num_coeffs', 20)

    freq_lims = kwargs.get('freq_lims', (80, 7800))

    win_len = kwargs.get('win_len', None)
    time_step = kwargs.get('time_step', None)

    use_power = kwargs.get('use_power', True)

    num_cores = kwargs.get('num_cores', 1)

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
    output_values = []
    total_mappings = len(path_mapping)
    cache = {}
    if match_function == 'xcorr':
        dist_func = xcorr_distance
    elif match_function == 'dct':
        dist_func = dct_distance
    else:
        dist_func = dtw_distance

    if rep == 'envelopes':
        if use_window:
            to_rep = partial(to_envelopes,
                                        num_bands=num_filters,
                                        freq_lims=freq_lims,
                                        window_length=win_len,
                                        time_step=time_step)
        else:
            to_rep = partial(to_envelopes,num_bands=num_filters,freq_lims=freq_lims)
    elif rep == 'mfcc':
        to_rep = partial(to_mfcc,freq_lims=freq_lims,
                                    num_coeffs=num_coeffs,
                                    num_filters = num_filters,
                                    win_len=win_len,
                                    time_step=time_step,
                                    use_power = use_power)
    elif rep == 'mhec':
        to_rep = partial(to_mhec, freq_lims=freq_lims,
                                    num_coeffs=num_coeffs,
                                    num_filters = num_filters,
                                    window_length=win_len,
                                    time_step=time_step,
                                    use_power = use_power)
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


    cache = generate_cache(path_mapping, to_rep, num_cores)
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
    output_val = sum([x[1] for x in output]) / len(output)

    threaded_q = kwargs.get('threaded_q', None)
    if not threaded_q:
        return output_val
    else:
        threaded_q.put(output_val)
        return None

def analyze_directory(directory, **kwargs):

    if not os.path.isdir(directory):
        raise(ValueError('%s is not a directory.' % directory))

    files = os.listdir(directory)

    path_mapping = [ (os.path.join(directory,x),
                        os.path.join(directory,y))
                        for x in files
                        for y in files if x != y]
    return acoustic_similarity_mapping(path_mapping, **kwargs)

def rep_worker(job_q,return_dict,rep_func):
    while True:
        try:
            filename = job_q.get(timeout=1)
        except Empty:
            break
        rep = rep_func(filename)
        return_dict[os.path.split(filename)[1]] = rep

def generate_cache(path_mapping,rep_func,num_procs):
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
                      return_dict,rep_func))
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

def calc_asim(path_mapping, cache,dist_func,num_procs):
    if len(path_mapping[0]) == 3:
        axb = True
    else:
        axb = False

    job_queue = Queue()

    for pm in path_mapping:
        job_queue.put(pm)

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
    time.sleep(10)
    for p in procs:
        p.join()

    return return_dict

