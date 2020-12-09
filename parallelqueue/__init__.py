"""
The module :code:`parallelqueue` provides the basic processes used in parallel queue models.
"""
from parallelqueue.components import GeneralArrivals, Job, JobRouter
from parallelqueue.base_models import ParallelQueueSystem

__all__ = [GeneralArrivals, Job, JobRouter]

print("Depreciation Warning: The old implementation of `JSQd` fixed to Markov arrivals and \n"
      "service has been renamed `OldJSQSystem` and will be removed next release.")
