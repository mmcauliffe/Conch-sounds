import sys
import os
from setuptools import setup
from setuptools.command.test import test as TestCommand

import conch


def readme():
    with open('README.md') as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '-x', '--tb=long', 'tests']
        if os.environ.get('TRAVIS', False):
            self.test_args.insert(0, '--runslow')
        self.test_suite = True

    def run_tests(self):
        if __name__ == '__main__':  # Fix for multiprocessing infinite recursion on Windows
            import pytest
            errcode = pytest.main(self.test_args)
            sys.exit(errcode)


if __name__ == '__main__':
    setup(name='conch-sounds',
          version=conch.__version__,
          description='Analyze acoustic similarity in Python',
          classifiers=[
              'Development Status :: 3 - Alpha',
              'Programming Language :: Python',
              'Programming Language :: Python :: 3',
              'Operating System :: OS Independent',
              'Topic :: Scientific/Engineering',
              'Topic :: Text Processing :: Linguistic',
          ],
          keywords='phonetics, acoustics similarity',
          url='https://github.com/mmcauliffe/Conch',
          download_url='https://github.com/mmcauliffe/Conch/tarball/{}'.format(
              conch.__version__),
          author='Michael McAuliffe',
          author_email='michael.e.mcauliffe@gmail.com',
          packages=['conch',
                    'conch.analysis',
                    'conch.analysis.amplitude_envelopes',
                    'conch.analysis.formants',
                    'conch.analysis.intensity',
                    'conch.analysis.mfcc',
                    'conch.analysis.pitch',
                    'conch.distance'],
          package_data={'conch.analysis.pitch': ['*.praat'],
                        'conch.analysis.formants': ['*.praat'],
                        'conch.analysis.intensity': ['*.praat'],
                        'conch.analysis.mfcc': ['*.praat']},
          install_requires=[
              'numpy',
              'scipy',
              'praatio ~= 5.0',
              'librosa',
              'pyraat'
          ],
          cmdclass={'test': PyTest},
          extras_require={
              'testing': ['pytest'],
          }
          )
