
class AcousticSimError(Exception):
    def __init__(self, value = None):
        if value is not None:
            self.value = value
        else:
            self.value = 'There was an error with acoustic similarity.'

    def __str__(self):
        return self.value

class NoWavError(AcousticSimError):
    def __init__(self, directory, files):
        self.value = 'No wav files were found.'
        self.main = self.value

        self.information = 'The directory \'{}\' did not contain any wav files.'.format(directory)
        self.details = 'The following files were found in {}:\n\n'.format(directory)
        for f in files:
            self.details += '{}\n'.format(f)
