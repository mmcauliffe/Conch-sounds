import sys
from setuptools import setup
from setuptools.command.test import test as TestCommand

import multiprocessing

import acousticsim

def readme():
    with open('README.md') as f:
        return f.read()


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = ['--strict', '--verbose', '--tb=long', 'tests']
        self.test_suite = True

    def run_tests(self):
        if __name__ == '__main__': #Fix for multiprocessing infinite recursion on Windows
            import pytest
            errcode = pytest.main(self.test_args)
            sys.exit(errcode)

setup(name='acousticsim',
      version=acousticsim.__version__,
      description = 'Analyze acoustic similarity in Python',
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'Topic :: Scientific/Engineering',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='phonetics acoustics similarity',
      url='https://github.com/mmcauliffe/python-acoustic-similarity',
      download_url = 'https://github.com/mmcauliffe/python-acoustic-similarity/tarball/{}'.format(acousticsim.__version__),
      author='Michael McAuliffe',
      author_email='michael.e.mcauliffe@gmail.com',
      packages=['acousticsim',
                'acousticsim.distance',
                'acousticsim.representations',
                'acousticsim.processing',
                'acousticsim.praat',
                'acousticsim.clustering'],
      package_data={'acousticsim.praat': ['*.praat']},
      dependency_links = ['https://github.com/kylebgorman/textgrid/tarball/master#egg=textgrid-1.0'],
      install_requires=[
            'numpy',
            'scipy',
            'scikit-learn',
            'networkx',
            'textgrid',
      ],
    cmdclass={'test': PyTest},
    extras_require={
        'testing': ['pytest'],
    }
      )
