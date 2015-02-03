from numpy import zeros,mean,std, sum, array,inf,isinf
import copy

from multiprocessing import Process, Manager, Queue
from queue import Empty

import time

def summed_sq_error(features,segment_ends):
    num_segs = len(segment_ends)
    seg_begin = 0
    sse = 0
    for l in range(0,num_segs):
        seg_end = segment_ends[l]
        #if num_segs == 28:
        #    print(l)
        #    print(seg_begin)
        #    print(seg_end)
        sse += seg_sse(features,seg_begin,seg_end)
        seg_begin = seg_end
    #print(sse)
    return sse

def seg_sse(features,seg_begin,seg_end):
    num_features = features.shape[1]
    ml = zeros((1,num_features))
    count = 0
    for t in range(seg_begin,seg_end):
        ml += features[t,:]
        count += 1
    ml /= count
    sse = 0
    for t in range(seg_begin,seg_end):
        sse += sum((features[t,:] - ml) ** 2)
    return sse

def sse_worker(job_q,return_dict,features, segment_set):
    while True:
        try:
            l = job_q.get(timeout=1)
        except Empty:
            break
        return_dict[segment_set[l]] = calc_boundary_removal_sse(features, segment_set, l)

def calc_boundary_removal_sse(features, segment_set, l):
    segment_temp = copy.deepcopy(segment_set)
    del segment_temp[l]
    if l == 0:
        begin = 0
    else:
        begin = segment_temp[l-1]
    return seg_sse(features,begin,segment_temp[l])

def generate_initial_cache(features,segment_set, num_procs):
    sse_cache = {}
    num_segments = len(segment_set)

    job_queue = Queue()

    for l in range(num_segments-1):
        job_queue.put(l)

    manager = Manager()
    return_dict = manager.dict()
    procs = []
    for i in range(num_procs):
        p = Process(
                target=sse_worker,
                args=(job_queue,
                      return_dict,features, segment_set))
        procs.append(p)
        p.start()
    time.sleep(2)
    for p in procs:
        p.join()
    return return_dict

def find_next_best_cached(features,segment_temp,sse_cache):
    segment_set = copy.deepcopy(segment_temp)
    available = filter(lambda x: x[0] != features.shape[0],sse_cache.items())
    seg_bound, min_delta_sse = min(available, key = lambda x: x[1])
    inverted = dict([[v,k] for k,v in enumerate(segment_set)])
    ind = inverted[seg_bound]
    del segment_set[ind]


    del sse_cache[seg_bound]

    if ind != 0:
        sse_cache[segment_set[ind-1]] = calc_boundary_removal_sse(features,segment_set,ind-1)

    if segment_set[ind] != features.shape[0]:
        sse_cache[segment_set[ind]] = calc_boundary_removal_sse(features,segment_set,ind)

    return min_delta_sse, segment_set, sse_cache

def to_segments(features, threshold = 0.1, return_means=False,debug=False):
    if debug:
        start_time = time.time()
        print(features.shape)
    num_frames, num_coeffs = features.shape
    L = {}
    segment_iter = {}
    seg_temp = list(range(1,num_frames+1))
    if debug:
        print('begin boundary removals')
        prev_time = time.time()

    sse_cache = generate_initial_cache(features,seg_temp, 6)
    for num_segments in range(num_frames-1,1,-1):
        if debug:
            cur = num_frames-1-num_segments
            if cur % 100 == 0:
                print('loop %d of %d' % (cur,num_frames-1))
        #L[num_segments],segment_iter[num_segments], sse_cache = find_next_best(features,seg_temp,sse_cache,1)
        L[num_segments],segment_iter[num_segments], sse_cache = find_next_best_cached(features,seg_temp,sse_cache)
        seg_temp = segment_iter[num_segments]
    if debug:
        print('greedy segmentation took %f seconds' % (time.time()-start_time))
        print('Finding threshold')
    Larray = array(list(L.values()))
    thresh = mean(Larray) + (threshold *std(Larray))
    if debug:
        print(mean(Larray))
        print(thresh)
    ks = list(segment_iter.keys())
    for i in range(max(ks),min(ks)-1,-1):
        if L[i] > thresh:
            if debug:
                print(i)
            optimal = segment_iter[i]
            break
    else:
        optimal = segment_iter[-1]
    if not return_means:
        return optimal
    seg_begin = 0
    segments = zeros((len(optimal),num_coeffs))
    for i in range(len(optimal)):
        seg_end = optimal[i]
        segments[i,:] = mean(features[seg_begin:seg_end,:],axis=0)
        seg_begin = seg_end
    return optimal,segments
