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
        cache = {}
        num_bands=config.num_bands.get_value()
        freq_lims = (config.min_freq.get_value(),config.max_freq.get_value())
        window_length = config.window_length.get_value()
        time_step = config.time_step.get_value()
        use_praat = config.use_praat.get_value()
        num_coeffs = config.num_coeffs.get_value()
        num_bands = config.num_bands.get_value()
        use_window = config.use_window.get_value()
        use_power = config.use_power.get_value()
        use_segments = config.use_segments.get_value()

        if config.representation == 'envelopes':
            if use_window:
                to_rep = partial(to_envelopes,
                                            num_bands=num_bands,
                                            freq_lims=freq_lims,
                                            window_length=window_length,
                                            time_step=time_step)
            else:
                to_rep = partial(to_envelopes,num_bands=num_bands,freq_lims=freq_lims)
        elif config.representation == 'mfcc':
            to_rep = partial(to_mfcc,freq_lims=freq_lims,
                                        num_coeffs=num_coeffs,
                                        num_filters = num_bands,
                                        win_len=window_length,
                                        time_step=time_step,
                                        use_power = use_power)
        elif config.representation == 'mhec':
            to_rep = partial(to_mhec, freq_lims=freq_lims,
                                        num_coeffs=num_coeffs,
                                        num_filters = num_bands,
                                        window_length=window_length,
                                        time_step=time_step,
                                        use_power = use_power)
        #elif config.representation == 'gammatone':
            #if use_window:
                #to_rep = partial(to_gammatone_envelopes,num_bands = num_bands,
                                                    #freq_lims=freq_lims,
                                                    #window_length=window_length,
                                                    #time_step=time_step)
            #else:
                #to_rep = partial(to_gammatone_envelopes,num_bands = num_bands,
                                                    #freq_lims=freq_lims)
        #elif config.representation == 'melbank':
            #to_rep = partial(to_melbank,freq_lims=freq_lims,
                                        #win_len=window_length,
                                        #time_step=time_step,
                                        #num_filters = num_bands)
        #elif config.representation == 'prosody':
            #to_rep = partial(to_prosody,time_step=time_step)

        if config.match_algorithm == 'xcorr':
            dist_func = xcorr_distance
        elif config.match_algorithm == 'dtw':
            dist_func = dtw_distance
        #elif config.match_algorithm == 'dct':
            #dist_func = dct_distance

        asim = {}
        for pm in self.mapping:
            filetup = tuple(map(lambda x: os.path.split(x)[1],pm))
            if pm[0] not in cache:
                cache[pm[0]] = to_rep(pm[0])

                if use_segments and cache[pm[0]] is not None:
                    cache[pm[0]] = to_segments(cache[pm[0]])
            if pm[1] not in cache:
                cache[pm[1]] = to_rep(pm[1])

                if use_segments and cache[pm[1]] is not None:
                    cache[pm[1]] = to_segments(cache[pm[1]])
            if pm[2] not in cache:
                cache[pm[2]] = to_rep(pm[2])

                if use_segments and cache[pm[2]] is not None:
                    cache[pm[2]] = to_segments(cache[pm[2]])

            base = cache[pm[0]]
            model = cache[pm[1]]
            shadow = cache[pm[2]]


            if base is None:
                continue
            if model is None:
                continue
            if shadow is None:
                continue
            dist1 = dist_func(base,model)
            if dist1 == 0 or isnan(dist1):
                print(base)
                print(model)
                print(dist1)
                print(dist2)
                raise(ValueError)
            dist2 = dist_func(shadow,model)
            if isnan(dist2):
                print(base)
                print(model)
                print(dist1)
                print(dist2)
                raise(ValueError)
            if config.use_similarity:
                dist1 = 1/dist1
                dist2 = 1/dist2
            ratio = dist2 / dist1
            asim[filetup] = ratio

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


