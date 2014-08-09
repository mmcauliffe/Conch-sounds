from numpy import zeros,mean,std, sum, array,inf,isinf
import copy

def summed_sq_error(features,segment_ends):
    num_segs = len(segment_ends)
    num_features = features.shape[1]
    seg_begin = 0
    sse = 0
    for l in range(1,num_segs):
        seg_end = segment_ends[l]
        #if num_segs == 28:
        #    print(l)
        #    print(seg_begin)
        #    print(seg_end)
        ml = zeros((1,num_features))
        count = 0
        for t in range(seg_begin,seg_end):
            ml += features[t,:]
            count += 1
        ml /= count
        for t in range(seg_begin,seg_end):
            sse += sum((features[t,:] - ml) ** 2)
        seg_begin = seg_end
    #print(sse)
    return sse

def to_segments(features,debug=True):
    #print(features.shape)
    thresh = 0.5
    num_frames, num_coeffs = features.shape
    L = {}
    segment_iter = {}
    seg_temp = list(range(1,num_frames+1))
    old_sse = summed_sq_error(features,seg_temp)
    current_sse = old_sse
    for num_segments in range(num_frames-1,1,-1):
        best = []
        min_delta_sse = inf
        for l in range(num_segments):
            segment_set = copy.deepcopy(seg_temp)
            del segment_set[l]
            sse = summed_sq_error(features,segment_set)
            delta_sse = sse - old_sse
            if delta_sse < min_delta_sse:
                best = segment_set
                curent_sse = sse
                min_delta_sse = delta_sse
        if isinf(min_delta_sse):
            continue
        segment_iter[num_segments] = best
        seg_temp = best
        L[num_segments] = min_delta_sse
        old_sse = current_sse
    print(L)
    Larray = array(list(L.values()))
    threshold = mean(Larray) + (thresh *std(Larray))
    ks = list(segment_iter.keys())
    for i in range(max(ks),min(ks)-1,-1):
        #print(L[i])
        #print(i)
        if L[i] > threshold:
            optimal = segment_iter[i]
            break
    else:
        optimal = segment_iter[-1]
    if debug:
        return optimal
    #print(optimal)
    seg_begin = 0
    segments = zeros((len(optimal),num_coeffs))
    for i in range(len(optimal)):
        seg_end = optimal[i]
        segments[i,:] = mean(features[seg_begin:seg_end,:],axis=0)
        seg_begin = seg_end
    #print(segments)
    #raise(ValueError)
    return segments
