from numpy import log, sqrt, sum, correlate,argmax
#from scipy.signal import correlate,correlate2d,fftconvolve

def xcorr_distance(rep_one,rep_two):
    rep_one_saved = rep_one
    rep_two_saved = rep_two
    rep_one = rep_one.to_array()
    rep_two = rep_two.to_array()
    length_diff = rep_one.shape[0] - rep_two.shape[0]
    if length_diff > 0:
        longerRep = rep_one
        shorterRep = rep_two
    else:
        longerRep = rep_two
        shorterRep = rep_one
    num_bands = longerRep.shape[1]
    matchSum = correlate(longerRep[:,0]/sqrt(sum(longerRep[:,0]**2)),shorterRep[:,0]/sqrt(sum(shorterRep[:,0]**2)),mode='valid')
    for i in range(1,num_bands):
        longerBand = longerRep[:,i]
        denom = sqrt(sum(longerBand**2))
        if denom == 0:
            print(rep_one_saved['filename'])
            print(rep_one.shape)
            print(rep_two_saved['filename'])
            print(rep_two.shape)
            print(shorterBand)
            continue
        longerBand = longerBand/denom
        shorterBand = shorterRep[:,i]
        denom = sqrt(sum(shorterBand**2))
        if denom == 0:
            print(rep_one_saved['filename'])
            print(rep_one.shape)
            print(rep_two_saved['filename'])
            print(rep_two.shape)
            print(shorterBand)
            continue
        shorterBand = shorterBand/denom
        temp = correlate(longerBand,shorterBand,mode='valid')
        matchSum += temp
    maxInd = argmax(matchSum)
    matchVal = abs(matchSum[maxInd]/num_bands)
    return 1/matchVal

#def fft_correlate_envelopes(e1,e2):
    #length_diff = e1.shape[0] - e2.shape[0]
    #if length_diff > 0:
        #longerEnv = e1
        #shorterEnv = e2
    #else:
        #longerEnv = e2
        #shorterEnv = e1
    #num_bands = longerEnv.shape[1]
    #matchSum = fftconvolve(longerEnv[:,0],shorterEnv[:,0][::-1],mode='valid')
    #for i in range(1,num_bands):
        #temp = fftconvolve(longerEnv[:,i],shorterEnv[:,i][::-1],mode='valid')
        #matchSum = [matchSum[j] + temp[j] for j in range(len(matchSum))]
    #matchVal = max(matchSum)/num_bands
    #return matchVal
