'''
Created on 2012-08-17

@author: michael
'''

#import mlpy,os,numpy as np
import subprocess

praatdir = "/home/michael/dev/MentalLexicon/Praat/"

tooldir = "/home/michael/Documents/Linguistics/Tools/"
praatexe =tooldir+"praat"
scriptName = "toCochlea.praat"

def analyzeWave(path):
    os.system(praatexe+" "+praatdir.replace(" ", "\ ")+scriptName+" "+path)

def readPraatOut():
    f = open(praatdir+"output/log.txt").read()
    output = []
    lines = f.splitlines()
    for i in xrange(len(lines)):
        lines[i] = lines[i].split("\t")
    for i in xrange(len(lines[0])):
        newline = []
        for j in xrange(len(lines)):
            newline.append(lines[j][i])
        output.append(np.array(newline))
    return output

def get_breaks(coch,win_len=10):
    neigh_dists = [mlpy.dtw_std(coch[i],coch[i-1],squared=False) for i in range(1,len(coch))]
    print neigh_dists
    average_neigh_dist = float(sum(neigh_dists))/float(len(neigh_dists))
    segs = []
    seg = []
    for i in range(1,len(coch)):
        if i-1 < win_len:
            start = 0
        else:
            start = i - win_len
        if i > len(coch) - win_len:
            end = len(coch)
        else:
            end = i + win_len
        neigh_dists = [mlpy.dtw_std(coch[j],coch[j-1],squared=False)
                            for j in range(start,i-1)] + [mlpy.dtw_std(coch[j],coch[j-1],squared=False)
                                                        for j in range(i+1,end)]
        average_neigh_dist = float(sum(neigh_dists))/float(len(neigh_dists))
        dist = mlpy.dtw_std(coch[i],coch[i-1],squared=False)
        if dist > average_neigh_dist:
            segs.append(seg)
            seg = []
        seg.append(coch[i])
    segs.append(seg)
    print [0.01*float(len(x)) for x in segs]
    print sum([0.01*float(len(x)) for x in segs])

def evalSim(cochOne,cochTwo,sBool=False):
    distMat = np.zeros((len(cochOne),len(cochTwo)))
    distMat[0][0] = mlpy.dtw_std(cochOne[0],cochTwo[0],squared=sBool)
    for i in xrange(1,len(cochOne)):
        distMat[i][0] = distMat[i-1][0] + mlpy.dtw_std(cochOne[i],cochTwo[0],squared=sBool)
    for j in xrange(1,len(cochTwo)):
        distMat[0][j] = distMat[0][j-1] + mlpy.dtw_std(cochOne[0],cochTwo[j],squared=sBool)
    for i in xrange(2,len(cochOne)):
        for j in xrange(2,len(cochTwo)):
            distMat[i][j] = min(distMat[i][j-1],distMat[i-1][j-1],distMat[i-1][j]) + mlpy.dtw_std(cochOne[i],cochTwo[j],squared=sBool)
    return distMat[len(cochOne)-1][len(cochTwo)-1]

if __name__ == '__main__':
    male_one_cot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Male/110/Subject110-male-baseline-a-cot.wav'
    male_one_toot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Male/110/Subject110-male-baseline-u-toot.wav'
    male_two_cot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Male/104/Subject104-male-baseline-a-cot.wav'
    male_two_toot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Male/104/Subject104-male-baseline-u-toot.wav'
    female_one_cot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Female/111/Subject111-female-baseline-a-cot.wav'
    female_one_toot = '/home/speecon/Documents/Data/Audio/ATI/Shadowers/Female/111/Subject111-female-baseline-u-toot.wav'
    com = ['praat','praatscripts/similarities.praat',male_one_cot,male_one_toot]
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "Male one cot vs toot"
    print stdout
    print stderr
    
    com = ['praat','praatscripts/similarities.praat',male_one_cot,male_two_cot]
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "Male one cot vs male two cot"
    print stdout
    print stderr
    
    com = ['praat','praatscripts/similarities.praat',male_one_cot,male_two_toot]
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "Male one cot vs male two toot"
    print stdout
    print stderr
    
    com = ['praat','praatscripts/similarities.praat',male_one_cot,female_one_cot]
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "Male one cot vs female one cot"
    print stdout
    print stderr
    
    com = ['praat','praatscripts/similarities.praat',male_one_cot,female_one_toot]
    p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
    stdout, stderr = p.communicate()
    print "Male one cot vs female one toot"
    print stdout
    print stderr
