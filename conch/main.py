import os
from multiprocessing import cpu_count

from conch.exceptions import ConchError, NoWavError
from conch.multiprocessing import generate_cache, calculate_distances, calculate_axb_ratio

from .analysis.segments import SegmentMapping


def acoustic_similarity_mapping(path_mapping, analysis_function, distance_function, stop_check=None, call_back=None):
    """Takes in an explicit mapping of full paths to .wav files to have
    acoustic similarity computed.

    Parameters
    ----------
    path_mapping : iterable of iterables
        Explicit mapping of full paths of .wav files, in the form of a
        list of tuples to be compared.


    Returns
    -------
    dict
        Returns a list of tuples corresponding to the `path_mapping` input,
        with a new final element in the tuple being the similarity/distance
        score for that mapping.

    """

    num_cores = int((3 * cpu_count()) / 4)
    segments = set()
    for x in path_mapping:
        segments.update(x)
    cache = generate_cache(segments, analysis_function, num_cores, call_back, stop_check)
    asim = calculate_distances(path_mapping, cache, distance_function, num_cores, call_back, stop_check)
    return asim


def acoustic_similarity_directories(directories, analysis_function, distance_function, stop_check=None, call_back=None):
    """
    Analyze many directories.

    Parameters
    ----------
    directories : list of str
        List of fully specified paths to the directories to be analyzed

    """

    files = []

    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0, len(directories))
        cur = 0
    for d in directories:
        if not os.path.isdir(d):
            continue
        if stop_check is not None and stop_check():
            return
        if call_back is not None:
            cur += 1
            if cur % 3 == 0:
                call_back(cur)

        files += [os.path.join(d, x) for x in os.listdir(d) if x.lower().endswith('.wav')]

    if len(files) == 0:
        raise (ConchError("The directories specified do not contain any wav files"))

    if call_back is not None:
        call_back('Mapping directories...')
        call_back(0, len(files) * len(files))
        cur = 0
    path_mapping = list()
    for x in files:
        for y in files:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if not x.lower().endswith('.wav'):
                continue
            if not y.lower().endswith('.wav'):
                continue
            if x == y:
                continue
            path_mapping.append((x, y))

    result = acoustic_similarity_mapping(path_mapping, analysis_function, distance_function, stop_check, call_back)
    return result


def acoustic_similarity_directory(directory, analysis_function, distance_function, stop_check=None, call_back=None):
    all_files = list()
    wavs = list()
    directories = list()
    for f in os.listdir(directory):
        path = os.path.join(directory, f)
        all_files.append(path)
        if f.lower().endswith('.wav'):
            wavs.append(path)
        if os.path.isdir(path):
            directories.append(path)
    if not wavs:
        return acoustic_similarity_directories(*directories, analysis_function, distance_function, stop_check,
                                               call_back)

    if call_back is not None:
        call_back('Mapping files...')
        call_back(0, len(wavs) * len(wavs))
        cur = 0
    path_mapping = list()
    for x in wavs:
        for y in wavs:
            if stop_check is not None and stop_check():
                return
            if call_back is not None:
                cur += 1
                if cur % 20 == 0:
                    call_back(cur)
            if x == y:
                continue
            path_mapping.append((x, y))
    result = acoustic_similarity_mapping(path_mapping, analysis_function, distance_function, stop_check, call_back)
    return result


def analyze_long_file(path, segments, analysis_function,
                      num_jobs=None, padding=None,
                      call_back=None, stop_check=None):
    segment_mapping = SegmentMapping()
    for s in segments:
        b = s[0]
        e = s[1]
        if len(s) > 2:
            c = s[2]
        else:
            c = 0
        segment_mapping.add_file_segment(path, b, e, c, padding=padding)
    if num_jobs is None:
        num_jobs = int((3 * cpu_count()) / 4)
    output_dict = generate_cache(segment_mapping, analysis_function, num_jobs,
                                 call_back, stop_check)
    return output_dict


def analyze_segments(segment_mapping, analysis_function,
                     num_jobs=None,
                     call_back=None, stop_check=None):
    if num_jobs is None:
        num_cores = int((3 * cpu_count()) / 4)
    else:
        num_cores = num_jobs
    output_dict = generate_cache(segment_mapping, analysis_function, num_cores,
                                 call_back, stop_check)
    return output_dict
