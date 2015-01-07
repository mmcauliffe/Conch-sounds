import os
import random

from numpy import inf

from acousticsim.tuning.classes import DataSet,Configuration

datasets = []

def ati_model_lookup(directory,model,word):
    gender = 'f'
    if model[0] == 'Male':
        gender = 'm'
    wav_path = '%s_subj%s_%s_%s.wav' % (gender, model[0], word[0],word[1])
    speaker_dir = os.path.join(directory,model[1],model[0])
    return os.path.join(speaker_dir,wav_path)

def ati_shadower_baseline_lookup(directory,shadower,word):
    production_dir = os.path.join(directory,shadower[1],shadower[0],'Baseline')
    wav_path = 'Subject%s-%s-%s-%s-%s.wav' % (shadower[0],shadower[1].lower(),
                                                'baseline',word[0],word[1])
    return os.path.join(production_dir,wav_path)

def ati_shadower_shadowed_lookup(directory,model,shadower,word,production):
    model_string = '-%s_subj%s-%s' % (model[1][0].lower(),model[0],model[2])
    prod = '%s_%s' % ('Shadow',model[1].lower())
    production_dir = os.path.join(directory,shadower[1],shadower[0],prod,model[0])
    wav_path = 'Subject%s-%s-%s%s-%s-%s.wav' % (shadower[0],shadower[1].lower(),
                                                'shadow',model_string,word[0],word[1])
    return os.path.join(production_dir,wav_path)

ati_lookups = {'Model': ati_model_lookup,
                'Baseline': ati_shadower_baseline_lookup,
                'Shadowed': ati_shadower_shadowed_lookup}

ati_words = [('a','cot'),
            ('a','pod'),
            ('a','sock'),
            ('a','sod'),
            ('a','tot'),
            ('i','deed'),
            ('i','key'),
            ('i','peel'),
            ('i','teal'),
            ('i','weave'),
            ('u','boot'),
            ('u','dune'),
            ('u','hoop'),
            ('u','toot'),
            ('u','zoo')]

ati_voicetype = {'225': ['mostattractive_CAL'],
                '243':['leasttypical_CAL'],
                '262':['mosttypical_CAL'],
                '278':['leastattractive_CAL'],
                '274':['mosttypical_CAL'],
                '304':['leastattractive_CAL'],
                '316':['leasttypical_CAL'],
                '321':['mostattractive_CAL']}

def jam_model_lookup(directory,model,word):
    return os.path.join(directory,'modeltalker_%s.wav' % word)

def jam_shadower_baseline_lookup(directory,shadower,word):
    return os.path.join(directory,'%s_%s1.wav' % (shadower,word))

def jam_shadower_shadowed_lookup(directory,shadower,model,word,production):
    return os.path.join(directory,'%s_%s2.wav' % (shadower,word))


jam_lookups = {'Model': jam_model_lookup,
                'Baseline': jam_shadower_baseline_lookup,
                'Shadowed': jam_shadower_shadowed_lookup}

def nz_model_lookup(directory,model,word):
    return os.path.join(directory,model,'%s.wav' % word)

def nz_shadower_baseline_lookup(directory,shadower,word):
    return os.path.join(directory,shadower,'%s_%s.wav' %(shadower,word))

def nz_shadower_shadowed_lookup(directory,model,shadower,word,production):
    return os.path.join(directory,shadower,'%s_%s%s.wav' %(shadower,word,production))

nz_lookups = {'Model': nz_model_lookup,
                'Baseline': nz_shadower_baseline_lookup,
                'Shadowed': nz_shadower_shadowed_lookup}

nz_words = ['air','ear',
        'bare','beer',
        'dare', 'dear',
        'fare','fear',
        'hair','hear',
        'pair','peer',
        'rarely','really',
        'share','sheer',
        'spare','spear']

nz_productions = ['1','2','3']

ati_dataset = DataSet(r'C:\Users\michael\Documents\Data\ATI',
                        ati_lookups,
                        ati_words,
                        additional_model_info = ati_voicetype)

nz_dataset = DataSet(r'C:\Users\michael\Documents\Data\NZDiph',
                        nz_lookups,
                        nz_words,
                        productions = nz_productions)

bestConfig = None
representations = ['mfcc']
match_algorithm = ['xcorr','dtw','dct']

use_ati = True
use_nz = True
use_aic = False

if use_aic:
    best = inf
else:
    best = 0
if use_ati and use_nz:
    LOG_PATH = r'C:\Users\michael\Documents\Tuning\atiNz_log.txt'
elif use_ati:
    LOG_PATH = r'C:\Users\michael\Documents\Tuning\ati_log.txt'
else:
    LOG_PATH = r'C:\Users\michael\Documents\Tuning\nz_log.txt'

if __name__ == '__main__':
    for i in range(2000):
        print('Iteration: ', i)
        rep = representations[random.randint(0,len(representations)-1)]
        alg = match_algorithm[random.randint(0,len(match_algorithm)-1)]
        config = Configuration(rep,alg)
        config.verify()
        print(config)
        output_values = []
        if use_ati:
            output_values.append(ati_dataset.analyze_config(config,use_aic = use_aic,num_cores=5))
        if use_nz:
            output_values.append(nz_dataset.analyze_config(config,use_aic = use_aic,num_cores=5))
        print(output_values)
        if use_aic and output_values[0] < best:
            best = output_values[0]
            print('New best: ',best)
            bestConfig = config
            with open(LOG_PATH,'a') as f:
                f.write('Score: %s\n' % ', '.join(map(str,output_values)))
                f.write(str(bestConfig))
                f.write('\n')
        elif not use_aic and abs(output_values[0]) > best:
            best = abs(output_values[0])
            print('New best: ',best)
            bestConfig = config
            with open(LOG_PATH,'a') as f:
                f.write('Score: %s\n' % ', '.join(map(str,output_values)))
                f.write(str(bestConfig))
                f.write('\n')

