import sys
import traceback


class ConchError(Exception):
    def __init__(self, value=None):
        if value is not None:
            self.value = value
        else:
            self.value = 'There was an error with Conch.'

    def __str__(self):
        return self.value


class ImproperPraatFunction(ConchError):
    pass


class NoWavError(ConchError):
    def __init__(self, directory, files):
        self.value = 'No wav files were found.'
        self.main = self.value

        self.information = 'The directory \'{}\' did not contain any wav files.'.format(directory)
        self.details = 'The following files were found in {}:\n\n'.format(directory)
        for f in files:
            self.details += '{}\n'.format(f)


class MfccError(ConchError):
    pass


class ConchPythonError(ConchError):
    """
    Exception wrapper around unanticipated exceptions to better display
    them to users.

    Parameters
    ----------
    exc : Exception
        Uncaught exception to be be output in a way that can be interpreted
    """

    def __init__(self, details):
        self.main = 'Something went wrong that wasn\'t handled by conch.'

        self.information = 'Please forward to the details below to the developers.'
        self.details = ''.join(details)

    def __str__(self):
        return '\n'.join([self.main, self.information, self.details])


class ConchPraatError(ConchError):
    pass

class FunctionMismatch(ConchError):
    pass