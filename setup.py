try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

def readme():
    with open('README.md') as f:
        return f.read()
        
setup(name='acousticsim',
      version='0.1',
      description='',
      long_description='',
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
      author='Michael McAuliffe',
      author_email='michael.e.mcauliffe@gmail.com',
      packages=['acousticsim', 
                'acousticsim.distance',
                'acousticsim.representations',
                'acousticsim.tuning'],
      install_requires=[
            'numpy',
            'scipy'
      ]
      )
