ParallelQueue
=============

[![Documentation Status](https://readthedocs.org/projects/parallelqueue/badge/?version=latest)](https://parallelqueue.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/ParallelQueue.svg)](https://badge.fury.io/py/ParallelQueue)

This repository hosts the "ParallelQueue" project which is currently in its early stages of development. 
This package aims to allow for easier implementation of novel parallel processing 
approaches in Python DES packages (especially SimPy).

Installation
------------
From PyPi:

`pip install parallelqueue`

From this repository:
```
git clone https://github.com/aarjaneiro/ParallelQueue
cd ParallelQueue
python setup.py install
```

Current Goals
-------------
1. Introduce more common models into `base_models`.
2. Optimize SimPy boilerplate common to all models by incorporating Cython.  
3. Incorporate https://github.com/tqdm/tqdm for better progress visualization and simulation parallelization.
