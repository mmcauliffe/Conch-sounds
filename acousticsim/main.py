import os
from multiprocessing import cpu_count
from collections import OrderedDict

import librosa
from scipy.io import wavfile
from functools import partial

from numpy import zeros

from acousticsim.representations import Envelopes, Mfcc

from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

from acousticsim.exceptions import AcousticSimError,NoWavError
from acousticsim.multiprocessing import generate_cache, generate_cache_rep, calc_asim, generate_cache_sig_dict
from acousticsim.helper import _build_to_rep, load_attributes

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
        Lewandowski (2012).
    output_sim : bool, optional
        If true (default), the function will return similarities (inverse distance).
        If false, distance measures will be returned instead.

    Returns
    -------
    list of tuples
        Returns a list of tuples corresponding to the `path_mapping` input,
        with a new final element in the tuple being the similarity/distance
        score for that mapping.

    """

    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)
    rep = kwargs.get('rep','mfcc')
    if callable(rep):
        to_rep = rep
    else:
        to_rep = _build_to_rep(**kwargs)

    if kwargs.get('use_multi',False):
        num_cores = kwargs.get('num_cores', 1)
        if num_cores == 0:
            num_cores = int((3*cpu_count())/4)
    else:
        num_cores = 1
    output_sim = kwargs.get('output_sim',False)

    match_function = kwargs.get('match_function', 'dtw')
    cache = kwargs.get('cache',None)
    if isinstance(match_function, str):
        if match_function == 'xcorr':
            dist_func = xcorr_distance
        elif match_function == 'dct':
            dist_func = dct_distance
        else:
            dist_func = dtw_distance
    elif callable(match_function):
        dist_func = match_function

    attributes = kwargs.get('attributes',dict())
    if cache is None:
        cache = generate_cache_rep(path_mapping, to_rep, attributes, num_cores, call_back, stop_check)

    asim = calc_asim(path_mapping,cache,dist_func, output_sim,num_cores, call_back, stop_check)
    if kwargs.get('return_rep',False):
        return asim, cache

    return asim

def acoustic_similarity_directories(directory_one, directory_two, **kwargs):
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
        Lewandowski (2012).
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

    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)

    files_one = [x for x in os.listdir(directory_one) if x.lower().endswith('.wav')]
    if len(files_one) == 0:
        raise(NoWavError(directory_one,os.listdir(directory_one)))
    files_two = [x for x in os.listdir(directory_two) if x.lower().endswith('.wav')]
    if len(files_two) == 0:
        raise(NoWavError(directory_two,os.listdir(directory_two)))
    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0,len(files_one)*len(files_two))
        cur = 0

    path_mapping = list()
    for x in files_one:
        for y in files_two:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            path_mapping.append((os.path.join(directory_one,x),
                        os.path.join(directory_two,y)))


    output = acoustic_similarity_mapping(path_mapping, **kwargs)
    if stop_check is not None and stop_check():
        return
    output_val = sum(output.values()) / len(output)

    if kwargs.get('return_all', False):
        output_val = output,output_val

    return output_val

def analyze_directories(directories, **kwargs):
    """
    Analyze many directories.

    Parameters
    ----------
    directories : list of str
        List of fully specified paths to the directories to be analyzed
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

    """
    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)

    files = []
    kwargs['attributes'] = dict()

    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0,len(directories))
        cur = 0
    for d in directories:
        if not os.path.isdir(d):
            continue
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 3 == 0:
                call_back(cur)

        files += [os.path.join(d,x) for x in os.listdir(d) if x.lower().endswith('.wav')]

        att_path = os.path.join(d,'attributes.txt')
        if os.path.exists(att_path):
            kwargs['attributes'].update(load_attributes(att_path))
    if len(files) == 0:
        raise(AcousticSimError("The directories specified do not contain any wav files"))


    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0,len(files)*len(files))
        cur = 0
    path_mapping = list()
    for x in files:
        for y in files:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if not x.lower().endswith('.wav'):
                continue
            if not y.lower().endswith('.wav'):
                continue
            if x == y:
                continue
            path_mapping.append((x,y))

    result = acoustic_similarity_mapping(path_mapping, **kwargs)
    return result

def analyze_directory(directory, **kwargs):
    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)

    kwargs['attributes'] = dict()
    all_files = list()
    wavs = list()
    directories = list()
    for f in os.listdir(directory):
        path = os.path.join(directory,f)
        all_files.append(path)
        if f.lower().endswith('.wav'):
            wavs.append(path)
        if os.path.isdir(path):
            directories.append(path)
    if not wavs:
        return analyze_directories(directories, **kwargs)

    att_path = os.path.join(directory,'attributes.txt')
    if os.path.exists(att_path):
        kwargs['attributes'].update(load_attributes(att_path))

    if call_back is not None:
        call_back('Mapping files...')
        call_back(0,len(wavs)*len(wavs))
        cur = 0
    path_mapping = list()
    for x in wavs:
        for y in wavs:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if x == y:
                continue
            path_mapping.append((x,y))
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
        extract_wav(path,os.path.join(output_path,'%d.wav' % i),begin_time,end_time)
        begin = s+1

def create_sig_dict(path, segments, padding = None):
    sig, sr = librosa.load(path, sr = None, mono = False)
    if len(sig.shape) > 1:
        channels = sig.shape[1]
        sig = sig.T
    else:
        channels = 1
    data = OrderedDict()
    for s in segments:
        b = s[0]
        e = s[1]
        if padding is not None:
            b -= padding
            if b < 0:
                b = 0
            e += padding
        begin = int(sr * b)

        end = int(sr * e)
        if channels > 1 and len(s) > 2:
            data[s] = sig[begin:end, s[2]]
        else:
            data[s] = sig[begin:end]
    del sig
    return data, sr

def analyze_long_file(path, segments, function,
                num_jobs = None, channel = 0, padding = None,
                call_back = None, stop_check = None):
    data, sr = create_sig_dict(path, segments, padding)
    function = partial(function, sr = sr, padding = padding)
    if num_jobs is None:
        num_cores = int((3*cpu_count())/4)
    else:
        num_cores = num_jobs
    output_dict = generate_cache_sig_dict(data, function, num_cores,
                                        call_back, stop_check)
    return output_dict
