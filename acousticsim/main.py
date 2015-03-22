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

    stop_check = kwargs.get('stop_check',None)
    call_back = kwargs.get('call_back',None)
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
    if match_function == 'xcorr':
        dist_func = xcorr_distance
    elif match_function == 'dct':
        dist_func = dct_distance
    else:
        dist_func = dtw_distance

    attributes = kwargs.get('attributes',dict())
    if cache is None:
        cache = generate_cache(path_mapping, to_rep, attributes, num_cores, call_back, stop_check)

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
        if os.path.isdir(f):
            directories.append(f)
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

class Counter(object):
    def __init__(self, initval=0):
        self.val = Value('i', initval)
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val.value += 1

    def value(self):
        with self.lock:
            return self.val.value

class Stopped(object):
    def __init__(self, initval=False):
        self.val = Value('i', initval)
        self.lock = Lock()

    def stop(self):
        with self.lock:
            self.val.value = True

    def stop_check(self):
        with self.lock:
            return self.val.value

def rep_worker(job_q,return_dict, counter,rep_func,attributes, stopped):
    while True:
        if stopped.stop_check():
            break
        counter.increment()
        try:
            filename = job_q.get(timeout=1)
        except Empty:
            break
        path, filelabel = os.path.split(filename)
        att = OrderedDict()
        att['filename'] = filelabel
        try:
            att.update(attributes[filelabel])
        except (KeyError, TypeError):
            pass
        true_label = os.path.split(path)[1]
        rep = rep_func(filename,attributes=att)
        rep._true_label = true_label
        return_dict[os.path.split(filename)[1]] = rep

class RepWorker(Process):
    def __init__(self, job_q, return_dict, rep_func, attributes, counter, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = rep_func
        self.attributes = attributes
        self.counter = counter
        self.stopped = stopped

    def run(self):
        while True:
            self.counter.increment()
            try:
                filename = self.job_q.get(timeout=1)
            except Empty:
                break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            path, filelabel = os.path.split(filename)
            att = OrderedDict()
            att['filename'] = filelabel
            try:
                att.update(self.attributes[filelabel])
            except (KeyError, TypeError):
                pass
            true_label = os.path.split(path)[1]
            rep = self.function(filename,attributes=att)
            rep._true_label = true_label
            self.return_dict[os.path.split(filename)[1]] = rep

        return


def call_back_worker(call_back, counter, max_value, stop_check):
    call_back(0, max_value)
    while True:
        if stop_check is not None and stop_check():
            break
        time.sleep(0.01)
        value = counter.value()
        if value > max_value - 5:
            break
        call_back(value)

def file_queue_adder(files,queue, stopped):
    while len(files) > 0:
        f = files.pop(0)
        if not f.lower().endswith('.wav'):
            continue
        while True:
            if stopped.stop_check():
                break
            try:
                queue.put(f,False)
                break
            except Full:
                pass

def generate_cache(path_mapping,rep_func, attributes,num_procs, call_back, stop_check):

    all_files = set()
    for pm in path_mapping:
        if stop_check is not None and stop_check():
            return
        all_files.update(pm)
    all_files = sorted(all_files)
    stopped = Stopped()
    job_queue = JoinableQueue(100)
    file_ind = 0
    while True:
        if file_ind == len(all_files):
            break
        try:
            job_queue.put(all_files[file_ind],False)
        except Full:
            break
        file_ind += 1
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    #if call_back is not None:
    #    call_back('Generating representations...')
    #    cb = Process(target = call_back_worker,
    #                args = (call_back, counter, len(all_files), stop_check))
    #    procs.append(cb)
    for i in range(num_procs):
        p = RepWorker(job_queue,
                      return_dict,rep_func,attributes, counter, stopped)
        procs.append(p)
        p.start()
    time.sleep(2)
    if call_back is not None:
        call_back('Generating representations...')
        prev = 0
    val = 0
    while True:
        if file_ind == len(all_files):
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        job_queue.put(all_files[file_ind])

        if call_back is not None:
            value = counter.value()
            call_back(value)
        file_ind += 1
    job_queue.join()
    time.sleep(2)

    for p in procs:
        p.join()

    return return_dict

def dist_worker(job_q,return_dict,counter,dist_func, output_sim,axb,cache, stopped):
    while True:
        if stopped.stop_check():
            break
        counter.increment()
        try:
            pm = job_q.get(timeout=1)
        except Empty:
            break
        filetup = tuple(map(lambda x: os.path.split(x)[1],pm))
        try:
            base = cache[filetup[0]]
            model = cache[filetup[1]]
            if axb:
                shadow = cache[filetup[2]]
        except KeyError:
            continue
        dist1 = dist_func(base,model)
        if axb:
            dist2 = dist_func(shadow,model)
            try:
                ratio = dist2 / dist1
            except ZeroDivisionError:
                ratio = -1
        else:
            ratio = dist1
        if output_sim:
            try:
                ratio = 1/ratio
            except ZeroDivisionError:
                ratio = 1
        return_dict[filetup] = ratio

def queue_adder(path_mapping,queue,stopped):
    while len(path_mapping) > 0:
        if stopped.stop_check():
            break
        pm = path_mapping.pop(0)
        while True:
            if stopped.stop_check():
                break
            try:
                queue.put(pm,False)
                break
            except Full:
                pass

def calc_asim(path_mapping, cache,dist_func, output_sim,num_procs, call_back, stop_check):
    if len(path_mapping[0]) == 3:
        axb = True
    else:
        axb = False

    job_queue = Queue()
    stopped = Stopped()

    job_p = Process(target=queue_adder,
                    args = (path_mapping,job_queue, stopped))
    job_p.start()
    time.sleep(2)
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    #if call_back is not None:
    #    call_back('Calculating acoustic similarity...')
    #    cb = Process(target = call_back_worker,
    #                args = (call_back, counter, len(path_mapping), stop_check))
    #    procs.append(cb)
    for i in range(num_procs):
        p = Process(
                target=dist_worker,
                args=(job_queue,
                      return_dict, counter,dist_func, output_sim,axb,cache, stopped))
        procs.append(p)
        p.start()
    time.sleep(2)
    if call_back is not None:
        call_back('Calculating acoustic similarity...')
        prev = 0
    val = 0
    while val < len(path_mapping) - 5:
        if stop_check is not None and stop_check():
            stopped.stop()
            break
        val = counter.value()
        if call_back is not None:
            if prev != val:
                call_back(val)
                prev = int(val)
    job_p.join()
    for p in procs:
        p.join()
    return return_dict

