import os
import sys
import traceback
from multiprocessing import Process, Manager, Queue, cpu_count, Value, Lock, JoinableQueue
import time
from queue import Empty, Full
from collections import OrderedDict
import librosa

from numpy import zeros

from functools import partial

from acousticsim.representations import Envelopes, Mfcc

from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

from acousticsim.exceptions import AcousticSimError, NoWavError, AcousticSimPythonError


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
                rep = self.function(filename, attributes=att)
                rep._true_label = true_label
                self.return_dict[filename] = rep
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return


class FileRepWorker(Process):
    def __init__(self, job_q, return_dict, rep_func, attributes, counter, stopped, ignore_errors):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = rep_func
        self.attributes = attributes
        self.counter = counter
        self.stopped = stopped
        self.ignore_errors = ignore_errors

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
                rep = self.function(filename, attributes=att)
                # rep._true_label = true_label
                self.return_dict[filename] = rep
            except Exception as e:
                if self.ignore_errors:
                    continue
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return


class FileWorker(Process):
    def __init__(self, job_q, return_dict, rep_func, counter, stopped, ignore_errors):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = rep_func
        self.counter = counter
        self.stopped = stopped
        self.ignore_errors = ignore_errors

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
            try:
                rep = self.function(filename)
                self.return_dict[filename] = rep
            except Exception as e:
                if self.ignore_errors:
                    continue
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return


class SigRepWorker(Process):
    def __init__(self, job_q, return_dict, rep_func, counter, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = rep_func
        self.counter = counter
        self.stopped = stopped

    def run(self):
        while True:
            self.counter.increment()
            try:
                key, sig = self.job_q.get(timeout=1)
            except Empty:
                break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            try:
                rep = self.function(signal=sig, begin=key[0])
                self.return_dict[key] = rep
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return


class SegmentWorker(Process):
    def __init__(self, job_q, return_dict, function, padding, counter, stopped):
        Process.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = function
        self.padding = padding
        self.counter = counter
        self.stopped = stopped

    def load_segment(self, path, begin, end, channel):
        if self.padding:
            begin -= self.padding
            end += self.padding
            if begin < 0:
                begin = 0
        duration = end - begin
        sig, sr = librosa.load(os.path.expanduser(path), sr=None, mono=False, offset=begin, duration=duration)
        return sig, sr

    def run(self):
        while True:
            self.counter.increment()
            try:
                seg = self.job_q.get(timeout=1)
            except Empty:
                break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            try:
                path, begin, end, channel = seg[:4]
                sig, sr = self.load_segment(path, begin, end, channel)
                rep = self.function(signal=sig, begin=begin, sr=sr, padding=self.padding)
                self.return_dict[seg] = rep
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
            filetup = tuple(map(lambda x: os.path.split(x)[1], pm))
            try:
                base = self.cache[filetup[0]]
                model = self.cache[filetup[1]]
                if self.axb:
                    shadow = self.cache[filetup[2]]
            except KeyError:
                continue
            try:
                dist1 = self.function(base, model)
                if self.axb:
                    dist2 = self.function(shadow, model)
                    try:
                        ratio = dist2 / dist1
                    except ZeroDivisionError:
                        ratio = -1
                else:
                    ratio = dist1
                if self.output_sim:
                    try:
                        ratio = 1 / ratio
                    except ZeroDivisionError:
                        ratio = 1
                self.return_dict[filetup] = ratio
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = AcousticSimPythonError(traceback.format_exception(*sys.exc_info()))

        return


def generate_cache_file_segments(file_segments, function, padding, num_procs, call_back, stop_check):
    stopped = Stopped()
    job_queue = JoinableQueue(100)
    seg_ind = 0
    all_segs = sorted(file_segments)
    while True:
        if seg_ind == len(all_segs):
            break
        try:
            job_queue.put(all_segs[seg_ind], False)
        except Full:
            break
        seg_ind += 1
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = SegmentWorker(job_queue, return_dict, function, padding, counter, stopped)
        procs.append(p)
        p.start()
    if call_back is not None:
        call_back('Generating representations...')

    while True:
        if seg_ind == len(all_segs):
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        job_queue.put(all_segs[seg_ind])

        if call_back is not None:
            value = counter.value()
            call_back(value)
        seg_ind += 1
    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        raise (return_dict['error'])
    return return_dict


def generate_cache_sig_dict(sig_dict, rep_func, num_procs, call_back, stop_check):
    stopped = Stopped()
    job_queue = JoinableQueue(100)
    sig_ind = 0
    all_sigs = sorted(sig_dict.items(), key=lambda x: x[0])
    while True:
        if sig_ind == len(all_sigs):
            break
        try:
            job_queue.put(all_sigs[sig_ind], False)
        except Full:
            break
        sig_ind += 1
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = SigRepWorker(job_queue, return_dict, rep_func, counter, stopped)
        procs.append(p)
        p.start()
    if call_back is not None:
        call_back('Generating representations...')

    while True:
        if sig_ind == len(all_sigs):
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        job_queue.put(all_sigs[sig_ind])

        if call_back is not None:
            value = counter.value()
            call_back(value)
        sig_ind += 1
    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        raise (return_dict['error'])
    return return_dict


def generate_cache(path_mapping, rep_func, num_procs, call_back, stop_check, ignore_errors=False):
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
            job_queue.put(all_files[file_ind], False)
        except Full:
            break
        file_ind += 1
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = FileWorker(job_queue,
                       return_dict, rep_func, counter, stopped, ignore_errors)
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
        raise (return_dict['error'])
    return return_dict


def generate_cache_rep(path_mapping, rep_func, attributes, num_procs, call_back, stop_check):
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
            job_queue.put(all_files[file_ind], False)
        except Full:
            break
        file_ind += 1
    manager = Manager()
    return_dict = manager.dict()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = RepWorker(job_queue,
                      return_dict, rep_func, attributes, counter, stopped)
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
        raise (return_dict['error'])
    return return_dict


def calc_asim(path_mapping, cache, dist_func, output_sim, num_procs, call_back, stop_check):
    try:
        if len(path_mapping[0]) == 3:
            axb = True
        else:
            axb = False
        mapping_gen = False
    except TypeError:
        axb = False
        mapping_gen = True
    job_queue = JoinableQueue(100)
    stopped = Stopped()
    map_ind = 0
    if mapping_gen:
        while True:
            try:
                pathmap = next(path_mapping)
                map_ind += 1
            except StopIteration:
                break
            try:
                job_queue.put(pathmap, False)
            except Full:
                break

    else:
        while True:
            if map_ind == len(path_mapping):
                break
            try:
                job_queue.put(path_mapping[map_ind], False)
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
        try:
            call_back(0, len(path_mapping))
        except TypeError:
            pass

    if mapping_gen:
        while True:
            try:
                pathmap = next(path_mapping)
            except StopIteration:
                break
            if stop_check is not None and stop_check():
                stopped.stop()
                time.sleep(1)
                break
            job_queue.put(pathmap)
            if call_back is not None:
                value = counter.value()
                call_back(value)
            map_ind += 1

    else:
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
        raise (return_dict['error'])
    return return_dict
