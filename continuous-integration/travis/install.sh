#!/bin/sh
set -e
#check to see if miniconda folder is empty
if [ ! -d "$HOME/miniconda/envs/test-environment" ]; then
  wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
  chmod +x miniconda.sh
  ./miniconda.sh -b -p $HOME/miniconda
  export PATH="$HOME/miniconda/bin:$PATH"
  conda config --set always_yes yes --set changeps1 no
  conda config --add channels dsdale24
  conda update -q conda
  conda info -a
  conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION atlas numpy scipy pytest scikit-learn networkx
  source activate test-environment
  pip install -q coveralls coverage
else
  echo "Miniconda already installed."
fi

if [ ! -f "$HOME/tools/praat" ]; then
  cd $HOME/downloads
  latestVer=$(curl -s 'http://nginx.org/en/download.html' |
   grep -o 'praat.+_linux64\.tar\.gz')
  echo "Found ${latestVer}"
  # Download.
  curl "http://www.fon.hum.uva.nl/praat/${latestVer}" > praat-latest.tar.gz
  tar -zxvf praat-latest.tar.gz
  mv praat $HOME/tools/praat
else
  echo "Praat already installed."
fi

if [ ! -f "$HOME/tools/reaper" ]; then
  cd $HOME/downloads
  git clone https://github.com/google/REAPER.git
  cd REAPER
  mkdir build
  cd build
  cmake ..
  make
  mv reaper $HOME/tools/reaper
else
  echo "Reaper already installed"
fi
