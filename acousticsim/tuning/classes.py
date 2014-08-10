import os
import random
from csv import DictReader, DictWriter
from collections import Counter
from functools import partial

import subprocess
import tempfile

from numpy import isnan,log

from scipy.stats.stats import pearsonr

from acousticsim.representations import to_envelopes, to_mfcc
from acousticsim.distance import dtw_distance, xcorr_distance, dct_distance

from acousticsim.main import acoustic_similarity_mapping


class DataSet(object):
    def __init__(self,directory,lookup_functions,words,productions = None,additional_model_info = None):
        self.lookups = lookup_functions
        self.model_dir = os.path.join(directory,'Models')
        self.shadower_dir = os.path.join(directory,'Shadowers')
        subdirs = os.listdir(self.model_dir)
        if 'Female' in subdirs:
            self.use_gender = True
            male_models = os.listdir(os.path.join(self.model_dir,'Male'))
            female_models = os.listdir(os.path.join(self.model_dir,'Female'))
            self.models = list(map(lambda x: [x,'Male'],male_models))
            self.models += list(map(lambda x: [x,'Female'],female_models))
            male_shadowers = os.listdir(os.path.join(self.shadower_dir,'Male'))
            female_shadowers = os.listdir(os.path.join(self.shadower_dir,'Female'))
            self.shadowers = list(map(lambda x: [x,'Male'],male_shadowers))
            self.shadowers += list(map(lambda x: [x,'Female'],female_shadowers))
        else:
            self.use_gender = False
            self.models = subdirs
            self.shadowers = os.listdir(self.shadower_dir)
        if productions is None:
            self.productions = ['Shadow']
        else:
            self.productions = productions
        if additional_model_info is not None:
            for i in range(len(self.models)):
                self.models[i] += additional_model_info[self.models[i][0]]
        self.words = words
        axb_files = [x for x in os.listdir(directory) if x.endswith('.txt')]
        self.mapping = self.generate_mapping()
        self.listenerResp = []
        for f in axb_files:
            with open(os.path.join(directory,f),'r') as csvfile:
                reader = DictReader(csvfile, delimiter = '\t')
                for line in reader:
                    tup = (line['BaselineFile'],line['ModelFile'],line['ShadowedFile'])
                    respLine = {
                            'axbtuple':tup,
                            'Shadower': line['Shadower'],
                            'Listener': line['Listener'],
                            'Word': line['Word'],
                            'Dependent': line['Dependent']}

                    try:
                        respLine['Model'] = line['Model']
                    except KeyError:
                        pass
                    self.listenerResp.append(respLine)


    def generate_mapping(self):
        path_mapping = []
        for w in self.words:
            for m in self.models:
                model_path = self.lookups['Model'](self.model_dir,m,w)
                if not os.path.exists(model_path):
                    continue
                for s in self.shadowers:
                    base_path = self.lookups['Baseline'](self.shadower_dir,s,w)
                    if not os.path.exists(base_path):
                        continue
                    for p in self.productions:
                        shad_path = self.lookups['Shadowed'](self.shadower_dir,m,s,w,p)
                        if not os.path.exists(shad_path):
                            continue
                        path_mapping.append((base_path,model_path,shad_path))
        return path_mapping

    def analyze_config(self,config, use_aic = False, num_cores = 1):

        kwarg_dict = config.to_kwargs()
        kwarg_dict['num_cores'] = num_cores

        asim = acoustic_similarity_mapping(self.mapping, **kwarg_dict)

        if use_aic:
            with tempfile.NamedTemporaryFile(mode='w',delete=False) as f:
            #with open('temp.txt','w') as f:
                tempname = f.name
                #tempname = 'temp.txt'
                header = [x for x in self.listenerResp[0].keys() if x != 'axbtuple'] + ['Independent']
                writer = DictWriter(f,header,delimiter='\t')
                writer.writerow({x:x for x in header})
                for line in self.listenerResp:
                    try:
                        line.update({'Independent': asim[line['axbtuple']]})
                        writer.writerow({k:v for k,v in line.items() if k != 'axbtuple'})
                    except KeyError:
                        pass

            scriptname = os.path.join(os.path.dirname(os.path.abspath(__file__)),'get_aic.r')
            com = ['Rscript',scriptname,tempname]
            p = subprocess.Popen(com,stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE)
            stdout, stderr = p.communicate()
            if stderr:
                print(com)
                print(stderr)

                raise(ValueError)
            output = str(stdout.decode()).strip()
            if output == 'LmerError':
                print(com)
                raise(ValueError)
            aic = float(output)
            os.remove(tempname)
            return aic

        x = []
        y = []
        for k,v in asim.items():

            resps = [l['Dependent'] for l in self.listenerResp if l['axbtuple'] == k]

            x.append(sum(resps)/len(resps))
            y.append(v)
        correlation = pearsonr(x,y)
        return correlation[0]

class Param(object):
    def __init__(self,min_value,max_value,step):
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.reset_value()

    def reset_value(self):
        if isinstance(self.max_value,float):
            self.value = random.randint(0, int((self.max_value - self.min_value) / self.step)) * self.step + self.min_value
        elif isinstance(self.max_value,bool):
            self.value = bool(random.randint(0,1))
        else:
            self.value = random.randrange(self.min_value,self.max_value,self.step)

    def get_value(self):
        return self.value

class Configuration(object):
    max_freq = Param(4000,8000,100)
    min_freq = Param(50,500,50)
    window_length = Param(0.005,0.05,0.005)
    time_step = Param(0.001,0.01,0.001)
    use_praat = Param(True,False,1)
    num_coeffs = Param(10,30,2)
    use_power = Param(False,True,1)
    num_bands = Param(4,48,2)
    use_window = Param(True,False,1)
    use_segments = Param(True,False,1)
    use_similarity = Param(True,False,1)

    def __init__(self,representation,match_algorithm):
        self.representation = representation
        self.match_algorithm = match_algorithm
        self.max_freq.reset_value()
        self.min_freq.reset_value()
        self.window_length.reset_value()
        self.time_step.reset_value()
        self.use_praat.value = False
        self.num_coeffs.reset_value()
        self.use_power.reset_value()
        self.num_bands.reset_value()
        self.use_window.reset_value()
        self.use_segments.reset_value()
        self.use_segments.value = False
        self.use_window.value = True
        self.use_similarity.reset_value()
        #self.representation = 'mfcc'
        #self.match_algorithm = 'dct'
        #self.min_freq.value = 450
        #self.max_freq.value = 5000
        #self.window_length.value = 0.05
        #self.time_step.value = 0.01
        #self.num_coeffs.value = 14
        #self.num_bands.value = 40
        #self.use_power.value = True

    def verify(self):
        if self.representation in ['mfcc','mhec']:
            while self.num_coeffs.get_value() >= self.num_bands.get_value():
                self.num_coeffs.reset_value()
                self.num_bands.reset_value()
        elif self.representation == 'envelopes':
            while self.num_bands.get_value() > 20:
                self.num_bands.reset_value()
        while self.window_length.get_value() <= self.time_step.get_value():
            self.window_length.reset_value()
            self.time_step.reset_value()

    def to_kwargs(self):
        kwarg_dict = {}
        kwarg_dict['rep'] = self.representation
        kwarg_dict['match_algorithm'] = self.match_algorithm
        kwarg_dict['num_filters']=self.num_bands.get_value()
        kwarg_dict['freq_lims'] = (self.min_freq.get_value(),self.max_freq.get_value())
        kwarg_dict['win_len'] = self.window_length.get_value()
        kwarg_dict['time_step'] = self.time_step.get_value()
        kwarg_dict['num_coeffs'] = self.num_coeffs.get_value()
        kwarg_dict['use_power'] = self.use_power.get_value()

        return kwarg_dict

    def __str__(self):

        return '''
        Representation: %s
        Matching algorithm: %s
        Min freq: %d
        Max freq: %d
        Win len: %f
        Time step: %f
        Num coeffs: %d
        Num bands: %d
        Use power: %r
        Use Praat: %r
        Use window: %r
        Use segments: %r
        ''' % (self.representation,self.match_algorithm,self.min_freq.get_value(),
                self.max_freq.get_value(),self.window_length.get_value(),self.time_step.get_value(),
                self.num_coeffs.get_value(), self.num_bands.get_value(), self.use_power.get_value(),
                self.use_praat.get_value(),self.use_window.get_value(),self.use_segments.get_value())


class MfccConfig(Configuration):
    pass

class EnvelopeConfig(Configuration):
    pass

class MhecConfig(Configuration):
    pass

class GammatoneConfig(Configuration):
    pass

class MelBankConfig(Configuration):
    pass


