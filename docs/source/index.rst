ParallelQueue
##############
A SimPy Extension for parallel queueing systems and routing.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

    Introduction to SimPy and DES <simpy>
    Module Documentation <modoc>
    Examples <examples>

This package aims to allow for easier implementation of novel parallel processing
approaches in Python DES packages (especially SimPy).

Installation
------------
From PyPi:

:code:`pip install parallelqueue`

From git repository:

.. code::

    git clone https://github.com/aarjaneiro/ParallelQueue
    cd ParallelQueue
    python setup.py install


Current Goals
-------------
1. Introduce more common models into `base_models`.
2. Optimize SimPy boilerplate common to all models by incorporating Cython.
3. Incorporate https://github.com/tqdm/tqdm for better progress visualization and simulation parallelization.

Interested in Contributing?
---------------------------
Do feel free to write an issue or submit a PR! If you are interested co-maintaining this package with me, please email me at
ajstone@uwaterloo.ca (merely include a brief description of your familiarity with Python and Queueing Theory).


References
----------

..

    Heavy Traffic Analysis of the Mean Response Time forLoad Balancing Policies in the Mean Field Regime
        Tim Hellemans, Benny Van Houdt (2020)

        https://arxiv.org/abs/2004.00876

..

    Redundancy-d:The Power of d Choices for Redundancy
        Kristen Gardner, Mor Harchol-Balter, Alan Scheller-Wolf,
        Mark Velednitsky, Samuel Zbarsky (2020)

        https://doi.org/10.1287/opre.2016.1582





Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
