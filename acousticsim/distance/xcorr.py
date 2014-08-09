from numpy import log, sqrt, sum, correlate,argmax
#from scipy.signal import correlate,correlate2d,fftconvolve

def xcorr_distance(e1,e2):
    length_diff = e1.shape[0] - e2.shape[0]
    if length_diff > 0:
        longerEnv = e1
        shorterEnv = e2
    else:
        longerEnv = e2
        shorterEnv = e1
    num_bands = longerEnv.shape[1]
    matchSum = correlate(longerEnv[:,0]/sqrt(sum(longerEnv[:,0]**2)),shorterEnv[:,0]/sqrt(sum(shorterEnv[:,0]**2)),mode='valid')
    for i in range(1,num_bands):
        longerBand = longerEnv[:,i]
        denom = sqrt(sum(longerBand**2))
        longerBand = longerBand/denom
        shorterBand = shorterEnv[:,i]
        denom = sqrt(sum(shorterBand**2))
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
