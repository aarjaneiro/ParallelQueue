ParallelQueue
=============

[![Documentation Status](https://readthedocs.org/projects/parallelqueue/badge/?version=latest)](https://parallelqueue.readthedocs.io/en/latest/?badge=latest)
[![PyPI version](https://badge.fury.io/py/ParallelQueue.svg)](https://badge.fury.io/py/ParallelQueue)
[![GitHub release](https://img.shields.io/github/v/release/aarjaneiro/parallelqueue?include_prereleases&label=GitHub&logo=github)](https://github.com/aarjaneiro/ParallelQueue)

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

Interested in Contributing?
---------------------------
Do feel free to write an issue or submit a PR! If you are interested co-maintaining this package with me, please email me at
ajstone@uwaterloo.ca (merely include a brief description of your familiarity with Python and Queueing Theory).

Also, be sure to look into the development branches!

References
----------
    Heavy Traffic Analysis of the Mean Response Time for 
    Load Balancing Policies in the Mean Field Regime
        Tim Hellemans, Benny Van Houdt (2020)
        https://arxiv.org/abs/2004.00876

    Redundancy-d:The Power of d Choices for Redundancy
        Kristen Gardner, Mor Harchol-Balter, Alan Scheller-Wolf,
        Mark Velednitsky, Samuel Zbarsky (2017)
        https://doi.org/10.1287/opre.2016.1582

Release Notes
-------------
0.0.6 will likely be the only release for the next few weeks. 
Next release is likely to include some of the above goals and monitoring tools.
