from linghelper.phonetics.praat import PraatLoader
from linghelper.phonetics.praat.helper import to_time_based_dict

from scipy.interpolate import interp1d

from numpy import vstack,array
    
def interpolate_pitch(pitch_track):
    defined_keys = [k for k in sorted(pitch_track.keys()) if pitch_track[k]['Pitch'] != '--undefined--']
    x = array(defined_keys)
    y = array([ pitch_track[k]['Pitch'] for k in defined_keys])
    if len(x) == 0:
        return None
    times = list(filter(lambda z: z >= min(x) and z <= max(x),defined_keys))
    f = interp1d(x,y)
    return f(times)

def get_intensity_spline(intensity_track):
    y = array([ intensity_track[k]['Intensity'] for k in sorted(intensity_track.keys()) if intensity_track[k]['Intensity'] != '--undefined--'])
    return y

def interpolate_prosody(pitch,intensity):
    defined_keys = [k for k in sorted(pitch.keys()) if pitch[k]['Pitch'] != '--undefined--']
    x = array(defined_keys)
    y = array([ pitch[k]['Pitch'] for k in defined_keys])
    if len(x) == 0:
        return None
    times = list(filter(lambda z: z >= min(x) and z <= max(x),defined_keys))
    p = interp1d(x,y)
    x = list(sorted(intensity.keys()))
    y =[intensity[k]['Intensity'] for k in x]
    i = interp1d(x, y)
    pitch_spline = p(times)
    intensity_spline = i(times)
    return vstack((pitch_spline,intensity_spline)).T
    
def to_pitch(filename,time_step):
    p = PraatLoader()
    output = p.run_script('pitch.praat', filename,time_step)
    try:
        pitch = to_time_based_dict(output)
    except IndexError:
        return None
    pitch_spline = interpolate_pitch(pitch)
    if pitch_spline is None:
        return None
    return pitch_spline.T
    
def to_intensity(filename,time_step):
    p = PraatLoader()
    output = p.run_script('intensity.praat', filename,time_step)
    intensity = to_time_based_dict(output)
    intensity_spline = get_intensity_spline(intensity)
    return intensity_spline.T

def to_prosody(filename,time_step):
    p = PraatLoader()
    output = p.run_script('pitch.praat', filename,time_step)
    try:
        pitch = to_time_based_dict(output)
    except IndexError:
        return None
    output = p.run_script('intensity.praat', filename,time_step)
    intensity = to_time_based_dict(output)
    prosody = interpolate_prosody(pitch,intensity)
    return prosody

    
    
