'''
Created on 2012-08-15

@author: michael
'''

from bulbs.neo4jserver import Graph,Config,NEO4J_URI
from models import Word,Segment,Similarity,Transcription

import re

def loadFile():
    f = open("/home/michael/Documents/Linguistics/Tools/FreqDicts/Iphod/iphod.txt").read().splitlines()
    head = f.pop(0)
    newlines = []
    for l in f:
        line = l.split("\t")
        stress = ''.join(re.findall(r'\d',line[2]))
        newlines.append([line[0],line[1],stress,line[3]])
    return newlines
    

if __name__ == '__main__':
    print NEO4J_URI
    #config = Config('http://localhost:7474/lexdb/data/')
    g = Graph()
    g.clear()
    g.add_proxy("words",Word)
    g.add_proxy('segments',Segment)
    g.add_proxy("transcribed_with",Transcription)
    g.add_proxy("similar_to",Similarity)
    w = g.vertices.create(name="hello")
    print g.V


    