import os
import sys
import traceback
from threading import Lock, Thread
from queue import Queue, Empty, Full
import time

from conch.exceptions import ConchPythonError


def default_njobs():
    import multiprocessing
    return int(0.75 * multiprocessing.cpu_count())


class Counter(object):
    def __init__(self, initval=0):
        self.val = initval
        self.lock = Lock()

    def increment(self):
        with self.lock:
            self.val += 1

    def value(self):
        with self.lock:
            return self.val


class ReturnDictionary(object):
    def __init__(self):
        self.val = {}
        self.lock = Lock()

    def __contains__(self, item):
        with self.lock:
            return item in self.val

    def value(self):
        with self.lock:
            return self.val

    def __setitem__(self, key, value):
        with self.lock:
            self.val[key] = value

    def __getitem__(self, item):
        with self.lock:
            return self.val[item]


class Stopped(object):
    def __init__(self, initval=False):
        self.val = initval
        self.lock = Lock()

    def stop(self):
        with self.lock:
            self.val = True

    def stop_check(self):
        with self.lock:
            return self.val


class AnalysisWorker(Thread):
    def __init__(self, job_q, return_dict, analysis_function, counter, stopped, ignore_errors=False):
        Thread.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = analysis_function
        self.counter = counter
        self.stopped = stopped
        self.ignore_errors = ignore_errors

    def run(self):
        while True:
            self.counter.increment()
            try:
                arguments = self.job_q.get(timeout=1)
            except Empty:
                break
            self.job_q.task_done()
            if self.stopped.stop_check():
                continue
            try:
                rep = self.function(arguments)
                self.return_dict[arguments] = rep
            except Exception as e:
                if self.ignore_errors:
                    continue
                self.stopped.stop()
                self.return_dict['error'] = arguments, ConchPythonError(traceback.format_exception(*sys.exc_info()))

        return


class DistanceWorker(Thread):
    def __init__(self, job_q, cache, return_dict, distance_function, counter, stopped):
        Thread.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = distance_function
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
            try:
                base = self.cache[pm[0]]
                model = self.cache[pm[1]]
                distance = self.function(base, model)
                self.return_dict[pm] = distance
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = (pm,ConchPythonError(traceback.format_exception(*sys.exc_info())))

        return


class AXBWorker(Thread):
    def __init__(self, job_q, cache, return_dict, distance_function, counter, stopped):
        Thread.__init__(self)
        self.job_q = job_q
        self.return_dict = return_dict
        self.function = distance_function
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
            try:
                a = self.cache[pm[0]]
                x = self.cache[pm[1]]
                b = self.cache[pm[2]]
            except KeyError:
                continue
            try:
                dist1 = self.function(a, x)
                dist2 = self.function(x, b)
                try:
                    ratio = dist2 / dist1
                except ZeroDivisionError:
                    ratio = -1
                self.return_dict[tuple(pm)] = ratio
            except Exception as e:
                self.stopped.stop()
                self.return_dict['error'] = (pm, ConchPythonError(traceback.format_exception(*sys.exc_info())))
        return


def generate_cache(segment_mapping, anaysis_function, num_procs, call_back, stop_check):
    stopped = Stopped()
    job_queue = Queue(100)
    seg_ind = 0
    num_segs = len(segment_mapping)
    segment_mapping = sorted(segment_mapping)
    while True:
        if seg_ind == num_segs:
            break
        try:
            job_queue.put(segment_mapping[seg_ind], False)
        except Full:
            break
        seg_ind += 1
    return_dict = ReturnDictionary()
    procs = []

    counter = Counter()
    for i in range(num_procs):
        p = AnalysisWorker(job_queue, return_dict, anaysis_function, counter, stopped)
        procs.append(p)
        p.start()
    if call_back is not None:
        call_back('Performing analysis...')

    while True:
        if seg_ind == num_segs:
            break
        if stop_check is not None and stop_check():
            stopped.stop()
            time.sleep(1)
            break
        job_queue.put(segment_mapping[seg_ind])

        if call_back is not None:
            value = counter.value()
            call_back(value)
        seg_ind += 1

    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        element, exc = return_dict['error']
        print(element)
        raise exc

    to_return = {}
    to_return.update(return_dict.value())
    return to_return


def calculate_distances(comparisons, cache, distance_function, num_jobs, call_back, stop_check):
    mapping_gen = not isinstance(comparisons, (list, tuple))
    job_queue = Queue(100)
    stopped = Stopped()
    map_ind = 0
    if mapping_gen:
        num_comparisons = 0
        while True:
            try:
                comp = next(comparisons)
                map_ind += 1
            except StopIteration:
                break
            try:
                job_queue.put(comp, False)
            except Full:
                break

    else:
        num_comparisons = len(comparisons)
        while True:
            if map_ind == num_comparisons:
                break
            try:
                job_queue.put(comparisons[map_ind], False)
            except Full:
                break
            map_ind += 1

    return_dict = ReturnDictionary()
    procs = []

    counter = Counter()
    for i in range(num_jobs):
        p = DistanceWorker(job_queue, cache,
                           return_dict, distance_function, counter, stopped)
        procs.append(p)
        p.start()

    if call_back is not None:
        call_back('Calculating acoustic distances...')
        try:
            call_back(0, num_comparisons)
        except TypeError:
            pass

    if mapping_gen:
        while True:
            try:
                pathmap = next(comparisons)
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
            if map_ind == num_comparisons:
                break
            if stop_check is not None and stop_check():
                stopped.stop()
                time.sleep(1)
                break
            job_queue.put(comparisons[map_ind])

            if call_back is not None:
                value = counter.value()
                call_back(value)
            map_ind += 1

    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        element, exc = return_dict['error']
        print(element)
        raise exc
    to_return = {}
    to_return.update(return_dict.value())
    return to_return


def calculate_axb_ratio(comparisons, cache, distance_function, num_jobs, call_back, stop_check):
    mapping_gen = not isinstance(comparisons, (list, tuple))
    job_queue = Queue(100)
    stopped = Stopped()
    map_ind = 0
    if mapping_gen:
        num_comparisons = 0
        while True:
            try:
                comp = next(comparisons)
                map_ind += 1
            except StopIteration:
                break
            try:
                job_queue.put(comp, False)
            except Full:
                break

    else:
        num_comparisons = len(comparisons)
        while True:
            if map_ind == num_comparisons:
                break
            try:
                job_queue.put(comparisons[map_ind], False)
            except Full:
                break
            map_ind += 1

    return_dict = ReturnDictionary()
    procs = []

    counter = Counter()
    for i in range(num_jobs):
        p = AXBWorker(job_queue, cache,
                      return_dict, distance_function, counter, stopped)
        procs.append(p)
        p.start()

    if call_back is not None:
        call_back('Calculating acoustic distances...')
        try:
            call_back(0, num_comparisons)
        except TypeError:
            pass

    if mapping_gen:
        while True:
            try:
                pathmap = next(comparisons)
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
            if map_ind == num_comparisons:
                break
            if stop_check is not None and stop_check():
                stopped.stop()
                time.sleep(1)
                break
            job_queue.put(comparisons[map_ind])

            if call_back is not None:
                value = counter.value()
                call_back(value)
            map_ind += 1

    job_queue.join()

    for p in procs:
        p.join()
    if 'error' in return_dict:
        element, exc = return_dict['error']
        print(element)
        raise exc
    return return_dict.value()
