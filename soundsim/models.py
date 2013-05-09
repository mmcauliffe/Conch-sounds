'''
Created on 2012-08-15

@author: michael
'''
from bulbs.model import Node,Relationship
from bulbs.property import String, Integer, Float


class Word(Node):
    element_type = 'word'
    
    orthography = String(nullable=False)
    frequency = Float()
    nd = Integer()
    fwnd = Float()
    
class Cocholeagram(Node):
    element_type = 'cochleagram'
    
    path_to_wave = String()
    

class Segment(Node):
    element_type = 'segment'
    name = String(nullable=False)
    
class Transcription(Relationship):
    label = 'transcribed_as'
    order = Integer()

class Similarity(Relationship):
    label = "is_like"
    score = Float()
    
class PhonologicalSimilarity(Similarity):
    label = 'sounds_like'
    
class OrthographicalSimilarity(Similarity):
    label = 'is_spelled_like'
    
class ContextualSimilarity(Similarity):
    label = 'has_contexts_like'
    
class PrecedingContextualSimilarity(ContextualSimilarity):
    label = 'has_preceding_contexts_like'
    
class FollowingContextualSimilarity(ContextualSimilarity):
    label = 'has_following_contexts_like'
    
class SemanticSimilarity(Similarity):
    label = 'has_meanings_like'