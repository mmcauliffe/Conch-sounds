
import os
import re
from collections import defaultdict

import numpy as np

#from numpy import mean, std, array, min, max, inf,sqrt, exp, pi
import numpy as np
import pylab as P

from acousticsim.representations.mfcc import Mfcc
from acousticsim.representations.amplitude_envelopes import Envelopes
from acousticsim.representations.gammatone import Gammatone
from acousticsim.representations.pitch import Pitch, Harmonicity

#Features:
#Amplitude (relative?), Spectral slope?

TIMIT_SEGMENT_SET_VCSIL = {'C':{'b','d','g','p','t','k','q','jh','ch','s','sh',
                    'z','zh','f','th','v','dh','hh','hv','ax-h'},
                'V':{'m','n','ng','em','en','eng','nx','l','r','w','y','el',
                    'iy','ih','eh','ey','ae','aa','aw','ay','ah','ao','oy','ow','uh',
                    'uw','ux','er','ax','ix','axr','dx'},
                'SIL':{'pau','epi','h#','bcl','dcl','gcl','pcl','tcl','kcl'}}

TIMIT_SEGMENT_SET = {'C':{'b','d','g','p','t','k','q','jh','ch','s','sh',
                    'z','zh','f','th','v','dh','hh'},
                'SIL':{'pau','epi',
                    'h#','bcl','dcl','gcl','pcl','tcl','kcl'},
                'S':{'m','n','ng','em','en','eng','nx','l','r','w','y',
                    'el','hv','ax-h','dx'},
                'V':{
                    'iy','ih','eh','ey','ae','aa','aw','ay','ah','ao','oy','ow','uh',
                    'uw','ux','er','ax','ix','axr'}}

BUCKEYE_SEGMENT_SET = {'C':{'p','t','k','b','d','g','ch','jh','th','dh',
                            's','z','sh','zh','f','v','hh','tq'},
                        'SIL':{'SIL'},
                        'S':{'m','n','ng','l','w','r','y','nx','en','em',
                            'eng','el','dx'},
                        'V':{'aa','ae','ay','aw','ao','oy','ow','eh','ey',
                            'er','ah','uw','uh','ih','iy',
                            'aan',
                            'aen','ayn','awn','aon','oyn','own','ehn','eyn',
                            'ern','ahn','uwn','ihn','iyn','uhn'}}

BUCKEYE_SEGMENT_SET_VCSIL = {'C':{'p','t','k','b','d','g','ch','jh','th','dh',
                            's','z','sh','zh','f','v','hh','tq',},
                        'V':{'aa','ae','ay','aw','ao','oy','ow','eh','ey',
                            'er','ah','uw','uh','ih','iy','m','n','ng','l',
                            'w','r','y','nx','en','em','eng','el','aan',
                            'aen','ayn','awn','aon','oyn','own','ehn','eyn',
                            'ern','ahn','uwn','ihn','iyn','uhn'},
                        'SIL':{'SIL'}}

TIMIT_DIR = r'C:\Users\michael\Documents\Data\TIMIT_fixed'
BUCKEYE_DIR = r'C:\Users\michael\Documents\Data\VIC\Speakers'

TIMIT_DRS = ['DR1','DR2','DR3','DR4','DR5','DR6','DR7','DR8']

def align_dialog_info(words, phones, wavs):
    dialogs = {}
    for p in words:
        name = os.path.splitext(os.path.split(p)[1])[0]
        dialogs[name] = {'words':p}
    for p2 in phones:
        name = os.path.splitext(os.path.split(p2)[1])[0]
        dialogs[name]['phones'] = p2
    for p3 in wavs:
        name = os.path.splitext(os.path.split(p3)[1])[0]
        dialogs[name]['wav'] = p3
    return dialogs

def read_phones(path, dialect = 'timit', sr = None):
    output = list()
    with open(path,'r') as file_handle:
        if dialect == 'timit':
            for line in file_handle:

                l = line.strip().split(' ')
                start = float(l[0])
                end = float(l[1])
                phone = l[2]
                if sr is not None:
                    start /= sr
                    end /= sr
                output.append([phone, start, end])
        elif dialect == 'buckeye':
            f = re.split("#\r{0,1}\n",file_handle.read())[1]
            flist = f.splitlines()
            begin = 0.0
            for l in flist:
                line = re.split("\s+\d{3}\s+",l.strip())
                end = float(line[0])
                label = re.split(" {0,1};| {0,1}\+",line[1])[0]
                output.append([label,begin,end])
                begin = end

        else:
            raise(NotImplementedError)
    return output

class SpeechClassifierLandmarks(object):
    _freq_lims = (80,4000)
    _num_bands = 4

    def __init__(self, parameters = 'timit'):
        pass

    def train(self,dialect = 'timit'):
        #assume training on TIMIT
        if dialect == 'timit':
            path = TIMIT_DIR
            train_dir = os.path.join(path, 'TRAIN')
            segment_set = TIMIT_SEGMENT_SET
            wrdExt = '.wrd'
            phnExt = '.phn'
        elif dialect == 'buckeye':
            train_dir = BUCKEYE_DIR
            segment_set = BUCKEYE_SEGMENT_SET
            wrdExt = '.words'
            phnExt = '.phones'

        words = []
        phones = []
        wavs = []
        for root, subdirs, files in os.walk(train_dir):
            for f in files:
                if f.lower().endswith(wrdExt):
                    words.append(os.path.join(root,f))
                elif f.lower().endswith(phnExt):
                    phones.append(os.path.join(root,f))
                elif f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        dialogs = align_dialog_info(words, phones,wavs)
        values = [defaultdict(list) for i in range(self._num_bands)]
        for (i,(d,info)) in enumerate(dialogs.items()):
            print(i,len(dialogs), d)
            ampenvs = Envelopes(info['wav'],self._freq_lims, self._num_bands)

            #self.update_range(ampenvs)
            phones = read_phones(info['phones'],sr=ampenvs.sampling_rate,dialect=dialect)
            previous = None
            for p in phones:
                #if p[0] in segment_set['V']:
                #    phone_class = 'V'
                #else:
                #    phone_class = 'NV'
                for k,v in segment_set.items():
                    if p[0] in v:
                        phone_class = k
                        break
                else:
                    continue
                print(p)
                bands = ampenvs[p[1],p[2]]
                P.plot(bands)
                P.show()
                break

class SpeechClassifier(object):
    """
    Classify a wav file into speech components. Currently doesn't have
    high accuracy

    Parameters
    ----------
    parameters : str
        Parameters to use for the classifier, can be 'timit', 'buckeye'
        or 'new'

    """
    _num_coeffs = 3
    _use_priors = True
    win_len = 0.025
    time_step = 0.01
    freq_lims = (80,4000)

    def __init__(self, parameters = 'timit'):
        self._states = ['V','C','SIL', 'S']
        if parameters == 'timit':
            self._guass_values = {'S': [106.69858295806942, 13.788101941585037,
                                    -2.7157271472866578, 10.436144308052297,
                                    -4.7651752344952119, 16.40640775462192,
                                    -0.20527335955567133, 10.849061304730101,
                                    -0.47118579058647031, 8.2687453916999427,
                                    0.37763342640775416, 9.433485919731508,
                                    1.7238440536507622, 12.415721048856815,
                                    -4.1644962118506568, 11.289866989968807,
                                    -1.087066518341647, 12.346358683908502,
                                    122.57544878814136, 98.409504759980436,
                                    5.5296286574132241, 4.825418319490506],
                                'C': [98.669101415828138, 12.969681154558939,
                                    -31.383989078115722, 15.356287596393775,
                                    -3.6024466565312148, 13.052742055994578,
                                    2.8805856059435517, 14.843254671285834,
                                    1.8735038149092653, 13.428119472685694,
                                    0.20547684191851148, 10.865016028080774,
                                    -1.1094621990978419, 21.253209202475396,
                                    4.5868033781563868, 16.109931025613381,
                                    -0.30797358082648352, 17.285745939222192,
                                    27.162001644890676, 86.296812928620383,
                                    -0.0012759997855903513, 3.6931402207970461],
                                'SIL': [67.260125656339383, 16.364258978070932,
                                    -23.994604651768732, 11.8282996527255,
                                    -4.1936611952894509, 12.377333899724508,
                                    0.1952864254960883, 20.186446606791733,
                                    -1.7874594107406285, 10.183650016903522,
                                    -1.24398059928302, 11.261290783446572,
                                    9.3859576265900202, 23.711655267287838,
                                    0.0062866497091458437, 14.195477763466464,
                                    -1.247745911984363, 17.131753916206851,
                                    25.216211813260664, 85.720055043911827,
                                    -0.94090835139375628, 4.0782367578024195],
                                'V': [121.79361965642315, 12.147622531365982,
                                    -10.568844151240489, 10.181818034234762,
                                    -9.0190738510271338, 18.72513361330407,
                                    -1.8221555596816867, 10.023815472882168,
                                    0.1786402424590863, 6.5160231749873745,
                                    0.52604413889141155, 8.1725722837946346,
                                    -5.9174582469826369, 10.497004578953135,
                                    -1.4707037149398738, 9.7730479831706152,
                                    1.2984439177165692, 9.7936713622437921,
                                    134.39679444095819, 109.7964618588956,
                                    5.8068054070370332, 4.6899801286927882]}
            self._ranges = [[30.120333629226856, 159.66897139827836],
                            [-77.835593153485163, 32.870167900828804],
                            [-69.726366723368699, 62.529506799142993],
                            [-77.474592423943136, 89.850673096664636],
                            [-62.107330271953956, 63.23772724196985],
                            [-74.249433084205918, 65.588485849292454],
                            [-127.00926808091104, 132.30046306413362],
                            [-87.65436477838243, 89.160571452999051],
                            [-113.44799223511505, 110.40706447575778],
                            [0.0, 592.59259259259261],
                            [-39.999565683801926, 26.048043267524864]]
            self._priors = {'SIL': 0.23807641179745634,
                        'S': 0.15020121253448,
                        'V': 0.37767202810265377,
                        'C': 0.23405034756540993}
            self._initial_probs = {'SIL': 1.0, 'S': 0.0, 'V': 0.0, 'C': 0.0}
            self._transitions = {'C': {'C': 0.07291775798847565,
                                    'V': 0.6127815610267155,
                                    'SIL': 0.15914091147197484,
                                    'S': 0.15515976951283394},
                                'V': {'C': 0.2669533725667723,
                                    'V': 0.06088727931190584,
                                    'SIL': 0.27451335445903124,
                                    'S': 0.39764599366229064},
                                'SIL': {'C': 0.8465709994994159,
                                    'V': 0.03153679292507926,
                                    'SIL': 0.019189053896212248,
                                    'S': 0.1027031536792925},
                                'S': {'C': 0.11725506876506452,
                                    'V': 0.6145611796398696,
                                    'SIL': 0.1881468878491422,
                                    'S': 0.08003686374592373}}
        elif parameters == 'buckeye':
            self._guass_values = {'V': [128.90264866566679, 15.14317575840515,
                                    1.4871098383116084, 10.323758763127435,
                                    -6.3106813016323215, 14.045080900462775],
                                'SIL': [86.76749073542328, 12.076001681199791,
                                    -18.785544623133003, 7.3577038261119636,
                                    4.9374633668260719, 10.317154208644],
                                'C': [112.54976709996274, 17.433637984244346,
                                    -22.861301032841272, 19.124160819690392,
                                    6.1901419921157217, 14.163979962615953],
                                'S': [115.88482662589307, 14.987730620486317,
                                    4.0720428025866937, 10.516924467062324,
                                    5.2798333599796852, 13.508389353927729]}
            self._ranges = [[42.310066393516529, 188.05789726778681],
                            [-79.370596330143442, 48.209406532240891],
                            [-75.96161099579318, 82.987855827814656]]
            self._priors = {'V': 0.4063921598826558,
                            'SIL': 0.16116159722743895,
                            'C': 0.2656405574321356,
                            'S': 0.16680568545776964}
            self._initial_probs = {'V': 0.2627450980392157,
                                'SIL': 0.35294117647058826,
                                'C': 0.15294117647058825,
                                'S': 0.23137254901960785}
            self._transitions = {'V': {'V': 0.08651136312395726,
                                    'SIL': 0.024600374261622402,
                                    'C': 0.4763550074401407,
                                    'S': 0.41253325517427963},
                                'SIL': {'V': 0.3940983122207039,
                                    'SIL': 0.06355947852420873,
                                    'C': 0.29848210658492447,
                                    'S': 0.24386010267016286},
                                'C': {'V': 0.5984959206381872,
                                    'SIL': 0.034218503106175024,
                                    'C': 0.21540913958428531,
                                    'S': 0.1518764366713524},
                                'S': {'V': 0.6420108304718991,
                                    'SIL': 0.03064562098777161,
                                    'C': 0.21645109775021149,
                                    'S': 0.11089245079011777}}
        else:
            self._guass_values = {x: [0 for i in range((self._num_coeffs*3+2)*2)]
                                        for x in self._states}
            self._ranges = [[np.inf,-np.inf] for x in range((self._num_coeffs*3+2))]
            self._priors = {x: 0 for x in self._states}
            self._transitions = {x: {y: 0 for y in self._states} for x in self._states}
            self._initial_probs = {x: 0 for x in self._states}

    def train_range(self, train_dir):
        wavs = []
        for root, subdirs, files in os.walk(train_dir):
            for f in files:
                if f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        for f in wavs:
            mfcc, pitch, harmonicity = self.get_features(f)
            self.update_range(mfcc, pitch, harmonicity)

    def get_features(self, path):
        mfcc = Mfcc(path, self.freq_lims, self._num_coeffs, 0.025,
                    0.01, num_filters = 26, use_power = True, deltas = True)
        pitch = Pitch(path, self.time_step, (75,600))
        pitch.process()
        harmonicity = Harmonicity(path, self.time_step, 75)
        harmonicity.process()
        return mfcc, pitch, harmonicity

    def update_range(self, mfcc, pitch, harmonicity):
        num_cc = self._num_coeffs
        if mfcc._deltas:
            num_cc *= 3
        coeffs = mfcc.to_array()
        for i in range(num_cc):
            t = coeffs[:,i]
            try:
                mini = np.min(t)
                if mini < self._ranges[i][0]:
                    self._ranges[i][0] = mini
            except:
                continue
            maxi = np.max(t)
            if maxi > self._ranges[i][1]:
                self._ranges[i][1] = maxi
        pitches = pitch.to_array()
        mini = np.min(pitches)
        if mini < self._ranges[num_cc][0]:
            self._ranges[num_cc][0] = mini
        maxi = np.max(pitches)
        if maxi > self._ranges[num_cc][1]:
            self._ranges[num_cc][1] = maxi
        harms = harmonicity.to_array()
        mini = np.min(harms)
        if mini < self._ranges[num_cc+1][0]:
            self._ranges[num_cc+1][0] = mini
        maxi = np.max(harms)
        if maxi > self._ranges[num_cc+1][1]:
            self._ranges[num_cc+1][1] = maxi


    def train(self,dialect = 'timit'):
        #assume training on TIMIT
        if dialect == 'timit':
            path = TIMIT_DIR
            train_dir = os.path.join(path, 'TRAIN')
            segment_set = TIMIT_SEGMENT_SET
            wrdExt = '.wrd'
            phnExt = '.phn'
        elif dialect == 'buckeye':
            train_dir = BUCKEYE_DIR
            segment_set = BUCKEYE_SEGMENT_SET
            wrdExt = '.words'
            phnExt = '.phones'

        words = []
        phones = []
        wavs = []
        for root, subdirs, files in sorted(os.walk(train_dir)):
            for f in files:
                if f.lower().endswith(wrdExt):
                    words.append(os.path.join(root,f))
                elif f.lower().endswith(phnExt):
                    phones.append(os.path.join(root,f))
                elif f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        dialogs = align_dialog_info(words, phones,wavs)
        values = [defaultdict(list) for i in range(self._num_coeffs*3+2)]
        for (i,(d,info)) in enumerate(dialogs.items()):
            print(i,len(dialogs), d)
            mfcc, pitch, harmonicity = self.get_features(info['wav'])
            self.update_range(mfcc, pitch, harmonicity)
            phones = read_phones(info['phones'],sr=mfcc.sampling_rate,dialect=dialect)
            previous = None
            for p in phones:
                #if p[0] in segment_set['V']:
                #    phone_class = 'V'
                #else:
                #    phone_class = 'NV'
                for k,v in segment_set.items():
                    if p[0] in v:
                        phone_class = k
                        break
                else:
                    continue
                if previous is None:
                    self._initial_probs[phone_class] += 1
                else:
                    self._transitions[previous][phone_class] += 1
                coeffs = mfcc[p[1],p[2]]
                for i in range(self._num_coeffs*3):
                    t = [x[i] for x in coeffs]
                    values[i][phone_class].extend(t)
                pitches = pitch[p[1],p[2]]
                t = [x for x in pitches]
                values[self._num_coeffs*3][phone_class].extend(t)

                harms = harmonicity[p[1],p[2]]
                t = [x for x in harms]
                values[self._num_coeffs*3+1][phone_class].extend(t)

                previous = phone_class
            #break
        #Find out the max of each value
        total = 0
        for k in self._guass_values.keys():
            #if k not in ['V','NV']:
            #    continue
            for i in range(self._num_coeffs*3+2):
                ind = i * 2
                self._guass_values[k][ind] = np.mean(values[i][k])
                self._guass_values[k][ind+1] = np.std(values[i][k])
            self._priors[k] = len(values[0][k])
            total += self._priors[k]
        for k,v in self._priors.items():
            self._priors[k] = v/total

        initial_total = sum(self._initial_probs.values())
        for k,v in self._initial_probs.items():
            self._initial_probs[k] = v/initial_total

        for k,v in self._transitions.items():
            k_total = sum(v.values())
            for k2, v2 in v.items():

                v[k2] = v2/k_total

    def calc_prob(self, feature_values, category,use_pitch_info):
        if self._use_priors:
            val = self._priors[category]
        else:
            val = 1 /len(self._states)
        for i in range(self._num_coeffs*3+2):
            if not use_pitch_info and i == self._num_coeffs*3+2:
                break
            ind = i * 2
            mean = self._guass_values[category][ind]
            var = self._guass_values[category][ind+1]**2
            val = feature_values[i]
            if isinstance(val, list):
                val = val[0]
            prob = np.exp(-1*(val-mean)**2/(2*var))/(np.sqrt(np.pi*var))
            val *= prob
        return val

    def predict(self,feature_values, use_pitch_info=False):
        if len(feature_values) != self._num_coeffs*3+2:
            return None
        best_value = 0
        best_cat = None
        for k in self._guass_values.keys():
            if k not in self._states:
                continue

            if self._priors[k] is None:
                return None
            val = self.calc_prob(feature_values, k,use_pitch_info)
            if val > best_value:
                best_value = val
                best_cat = k
        return best_cat

    def find_vowels(self, path, speaker_ranges, num_vowels = 1, debug = False):

        vnv = self.predict_file(path, norm_amp = True,
                            alg = 'bayes',use_segments=False,
                            new_range = speaker_ranges, debug = debug)
        #print(vnv)
        vowels = [[x[1],x[2]] for x in vnv if x[0] == 'V' and x[2] - x[1] > self.time_step*1.5]
        #print(vowels)
        if len(vowels) == 0:
            vowels = [[x[1],x[2]] for x in vnv if x[0] == 'S' and x[2] - x[1] > self.time_step*1.5]
        if len(vowels) == 0:
            vnv = self.predict_file(path, norm_amp = True,
                                alg = 'bayes',use_segments=False,
                                new_range = speaker_ranges, debug = debug,
                                use_pitch_info=True)
            vowels = [[x[1],x[2]] for x in vnv if x[0] == 'V' and x[2] - x[1] > self.time_step*1.5]

            if len(vowels) == 0:
                vowels = [[x[1],x[2]] for x in vnv if x[0] == 'S' and x[2] - x[1] > self.time_step*1.5]

        while len(vowels) > num_vowels:
            closest_dist = 1000
            closest = 0
            for i in range(1,len(vowels)):
                dist_to_prev = vowels[i][0] - vowels[i-1][1]
                if dist_to_prev < closest_dist:
                    closest_dist = dist_to_prev
                    closest = i
            vowels[closest][0] = vowels[closest-1][0]
            vowels = [ x for i,x in enumerate(vowels) if i != closest-1]
        vowels = { tuple(x):'V' for x in vowels}
        return vowels

    def predict_file(self,path, norm_amp = False, alg='viterbi', use_segments = False,
                    new_range=None, debug = False, use_pitch_info=False):

        mfcc, pitch, harmonicity = self.get_features(path)
        if new_range is not None:
            mfcc._ranges = new_range[:self._num_coeffs*3]

        if norm_amp:
            mfcc.norm_amp(self._ranges[:self._num_coeffs*3])
        output = list()
        if use_segments:
            if not mfcc.segment(0.1):
                return
            for times,s in sorted(mfcc._segments.items()):
                print(times,s)
                predicted = self.predict(s)
                output.append([predicted,times[0],times[1]])
            return output
        cur = ['NV',0,0]
        if alg == 'viterbi':
            viterb = self.viterbi(mfcc)
            print(viterb[0])
            for i, time in enumerate(mfcc.keys()):
                predicted = viterb[1][i]
                if cur[0] != predicted:
                    cur[2] = time
                    output.append(cur)
                    cur = [predicted,time,0]
            cur[2] = time
            output.append(cur)

            #otuput = viterb[1]
        else:
            for time,frame in mfcc.items():
                t = list(frame)
                p = pitch[time]
                if p is None:
                    p = 0
                h = harmonicity[time]
                if h is None:
                    h = -20
                t.extend([p,h])
                predicted = self.predict(t,use_pitch_info)
                if debug:
                    print(time,predicted,t)
                if cur[0] != predicted:
                    cur[2] = time
                    output.append(cur)
                    cur = [predicted,time,0]
            cur[2] = time
            output.append(cur)
        return output


    def test(self, debug = False, dialect = 'timit', norm_amp = True, classifier = 'hmm'):
        print('begin testing')
        #assume testing on TIMIT
        if debug:
            with open('debug.txt','w') as f:
                pass
        words = []
        phones = []
        wavs = []
        if dialect == 'timit':
            path = TIMIT_DIR
            test_dir = os.path.join(path, 'TEST')
            segment_set = TIMIT_SEGMENT_SET
            wrdExt = '.wrd'
            phnExt = '.phn'
        elif dialect == 'buckeye':
            test_dir = BUCKEYE_DIR
            segment_set = BUCKEYE_SEGMENT_SET
            wrdExt = '.words'
            phnExt = '.phones'
        for root, subdirs, files in os.walk(test_dir):
            for f in files:
                if f.lower().endswith(wrdExt):
                    words.append(os.path.join(root,f))
                elif f.lower().endswith(phnExt):
                    phones.append(os.path.join(root,f))
                elif f.lower().endswith('.wav'):
                    wavs.append(os.path.join(root,f))
        dialogs = align_dialog_info(words, phones,wavs)
        hits = 0
        total = 0
        cats = sorted(self._priors.keys())
        cats2ind = {x:i for i,x in enumerate(cats)}
        conf_matrix = np.zeros((len(cats),len(cats)))

        for (i,(d,info)) in enumerate(dialogs.items()):
            print(i,len(dialogs))
            mfcc = Mfcc(info['wav'], (80,7800), self._num_coeffs, 0.025,
                        0.01, num_filters = 26, use_power = True)
            if norm_amp:
                mfcc.norm_amp(*self._ranges[0])
            phones = read_phones(info['phones'],sr=mfcc.sampling_rate, dialect=dialect)
            if debug:
                with open('debug.txt','a') as f:
                    f.write('{}\n{}\n\n'.format(info['wav'],' '.join([x[0] for x in phones])))
            for p in phones:
                #if p[0] in segment_set['V']:
                #    phone_class = 'V'
                #else:
                #    phone_class = 'NV'
                for k,v in segment_set.items():
                    if p[0] in v:
                        phone_class = k
                        break
                else:
                    continue
                if debug:
                    with open('debug.txt','a') as f:
                        f.write('{}\n\n'.format(p))
                coeffs = mfcc[p[1],p[2]]
                for frame in coeffs:
                    predicted = self.predict(frame)
                    colInd = cats2ind[predicted]
                    rowInd = cats2ind[phone_class]
                    conf_matrix[rowInd,colInd] += 1
                    if predicted == phone_class:
                        hits += 1
                    total += 1
                    if debug:
                        with open('debug.txt','a') as f:
                            f.write('{}\t{}\t{}\n'.format(phone_class,predicted,' '.join(map(str,frame))))
            print('Current accuracy:',hits/total)
        print('Accuracy:',hits/total)
        print(cats)
        print(conf_matrix)

    def viterbi(self, mfcc):
        V = [{}]
        path = {}

        # Initialize base cases (t == 0)
        for y in self._states:
            V[0][y] = self._initial_probs[y] * self.calc_prob(mfcc.first(),y)
            path[y] = [y]

        # Run Viterbi for t > 0
        first = True
        for t,frame in enumerate(mfcc):
            if first:
                first = False
                continue
            V.append({})
            newpath = {}

            for y in self._states:
                (prob, state) = max((V[t-1][y0] * self._transitions[y0][y] * self.calc_prob(frame, y), y0) for y0 in self._states)
                print(prob, state)
                V[t][y] = prob
                newpath[y] = path[state] + [y]

            # Don't need to remember the old paths
            path = newpath
        n = 0           # if only one element is observed max is sought in the initialization values
        if len(mfcc) != 1:
            n = t
        #print_dptable(V)
        (prob, state) = max((V[n][y], y) for y in self._states)
        return (prob, path[state])

if __name__ == '__main__':
    sc = SpeechClassifier('new')
    #sc = SpeechClassifierLandmarks('new')
    sc.train(dialect = 'timit')
    #sc.test(dialect = 'timit',debug=False)
    with open('output_timit.txt','w') as f:
        print('Probability distributions',sc._guass_values, file=f)
        print('Ranges',sc._ranges, file=f)
        print('Priors',sc._priors, file=f)
        print('Initial probs',sc._initial_probs, file=f)
        print('Transitions',sc._transitions, file=f)

