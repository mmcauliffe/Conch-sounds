import os
import csv


def load_path_mapping(path):
    mapping = []
    with open(path, 'r', encoding='utf8') as f:
        dialect = csv.Sniffer().sniff(f.read(1024))
        f.seek(0)
        reader = csv.reader(f, dialect)
        for line in reader:
            for path in line:
                if not os.path.exists(path):
                    raise (OSError('The file path \'{}\' does not exist.'.format(path)))
            mapping.append(line)
    return mapping
