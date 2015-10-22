import os
import sys
import traceback
from multiprocessing import Process, Manager, Queue, cpu_count, Value, Lock, JoinableQueue
import time
from queue import Empty, Full
from collections import OrderedDict

from numpy import zeros

from functools import partial

from acousticsim.representations import Envelopes, Mfcc

from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

from acousticsim.exceptions import AcousticSimError,NoWavError, AcousticSimPythonError

def default_njobs():
    return int(0.75 * cpu_count())

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
            if not os.path.exists(filename):
                continue
            path, filelabel = os.path.split(filename)

            att = OrderedDict()
            att['filename'] = filelabel
            try:
                att.update(self.attributes[filelabel])
            except (KeyError, TypeError):
                pass
            true_label = os.path.split(path)[1]
            try:
                rep = self.function(filename,attributes=att)
                rep._true_label = true_label
                self.return_dict[os.path.split(filename)[1]] = rep
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return

class DistWorker(Process):
    def __init__(self, job_q, return_dict, counter, dist_func, output_sim, axb, cache, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = dist_func
        self.output_sim = output_sim
        self.axb = axb
        self.cache = cache
        self.counter = counter
        self.stopped = stopped

    def run(self):
        while True:
            self.counter.increment()
            try:
                pm = self.job_q.get(timeout=1)
            except Empty:
                break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            filetup = tuple(map(lambda x: os.path.split(x)[1],pm))
            try:
                base = self.cache[filetup[0]]
                model = self.cache[filetup[1]]
                if self.axb:
                    shadow = self.cache[filetup[2]]
            except KeyError:
                continue
            try:
                dist1 = self.function(base,model)
                if self.axb:
                    dist2 = self.function(shadow,model)
                    try:
                        ratio = dist2 / dist1
                    except ZeroDivisionError:
                        ratio = -1
                else:
                    ratio = dist1
                if self.output_sim:
                    try:
                        ratio = 1/ratio
                    except ZeroDivisionError:
                        ratio = 1
                self.return_dict[filetup] = ratio
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return

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
    for i in range(num_procs):
        p = RepWorker(job_queue,
                      return_dict,rep_func,attributes, counter, stopped)
        procs.append(p)
        p.start()
    if call_back is not None:
        call_back('Generating representations...')

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

    for p in procs:
        p.join()
    if 'error' in return_dict:
        raise(return_dict['error'])
    return return_dict

def calc_asim(path_mapping, cache,dist_func, output_sim,num_procs, call_back, stop_check):
    if len(path_mapping[0]) == 3:
        axb = True
    else:
        axb = False
    job_queue = JoinableQueue(100)
    stopped = Stopped()

    map_ind = 0
    while True:
        if map_ind == len(path_mapping):
            break
        try:
            job_queue.put(path_mapping[map_ind],False)
        except Full:
            break
        map_ind += 1

    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = DistWorker(job_queue,
                      return_dict, counter, dist_func, output_sim, axb, cache, stopped)
        procs.append(p)
        p.start()

    if call_back is not None:
        call_back('Calculating acoustic similarity...')
        call_back(0,len(path_mapping))

    while True:
        if map_ind == len(path_mapping):
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        job_queue.put(path_mapping[map_ind])

        if call_back is not None:
            value = counter.value()
            call_back(value)
        map_ind += 1

    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        raise(return_dict['error'])
    return return_dict

