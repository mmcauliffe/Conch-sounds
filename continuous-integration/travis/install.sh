#!/bin/sh
set -e
#check to see if miniconda folder is empty
if [ ! -d "$HOME/miniconda/miniconda/envs/test-environment" ]; then
  if [ ! -d "$HOME/miniconda/miniconda" ]; then
    wget http://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -O miniconda.sh
    chmod +x miniconda.sh
    ./miniconda.sh -b -p $HOME/miniconda/miniconda
  fi
  export PATH="$HOME/miniconda/miniconda/bin:$PATH"
  conda config --set always_yes yes --set changeps1 no
  conda update -q conda
  conda info -a
  conda create -q -n test-environment python=$TRAVIS_PYTHON_VERSION numpy pytest setuptools
  source activate test-environment
  pip install -q coveralls coverage
else
  echo "Miniconda already installed."
fi

if [ ! -f "$HOME/tools/praat" ]; then
  cd $HOME/downloads
  #FOR WHEN TRAVIS UPDATES TO A NEWER UBUNTU
  #latestVer=$(curl -s 'https://www.fon.hum.uva.nl/praat/download_linux.html' |
  # grep -Eo 'praat[0-9]+_linux64barren\.tar\.gz' | head -1)

  # Download.
  curl "https://www.fon.hum.uva.nl/praat/praat6151_linux64barren.tar.gz" > praat-latest.tar.gz
  tar -zxvf praat-latest.tar.gz
  mv praat_barren $HOME/tools/praat
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

if [ ! -d "$HOME/tools/autovot" ]; then
  cd $HOME/tools
  git clone https://github.com/mlml/autovot.git
  cd autovot/autovot/code
  make
else
  echo "AutoVOT already installed"
fi
