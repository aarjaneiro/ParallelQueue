import random

import pandas as pd
from simpy import Environment, Resource

from parallelqueue.components import PoissonArrivals


class RedundancyQueueSystem:
    """
    A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join, potentially replicating
    itself before enqueueing. For the sampled queues with sizes less than r, the job and/or its clones will join while awaiting
    service. After completing service, each job and its replicas are disposed of.

    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param arrivalMean: Mean of Poisson arrival process.
    :param maxTime: Runtime limit.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param df: Whether or not a pandas.DataFrame of the queue sizes over time should be returned.
    :param d: Number of queues to parse.
    :param meanServer: Mean servicing time.
    :param doPrint: If true, each event will trigger a statement to be printed.

    Example
    -------
    .. code-block:: python

        # Specifies a SimPy environment consisting
        # of a Redundancy-2 queueing system and a Poisson arrival process.
        sim = ParallelQueueSystem(arrivalMean=5, maxTime=100.0,
            parallelism=100, seed=1234, d=2, meanServer=1.0)
        sim.RunSim

    """

    def __init__(self, arrivalMean, maxTime, parallelism, seed, d, meanServer, r=None, doPrint=False, df=False,
                 infiniteJobs=True, numberJobs=0):
        self.infiniteJobs = infiniteJobs
        self.d = d
        self.doPrint = doPrint
        self.timeInBank = meanServer
        self.seed = seed
        self.r = r
        self.parallelism = parallelism
        self.maxTime = maxTime
        self.arrivalMean = arrivalMean
        self.ReplicaDict = {}
        self.Number = 0 if self.infiniteJobs else numberJobs
        self.queuesOverTime = []
        self.df = df

    def __SimManager(self):
        random.seed(self.seed)
        env = Environment()
        queues = {i: Resource(env) for i in range(self.parallelism)}

        env.process(PoissonArrivals(system=self, env=env, number=self.Number, interval=self.arrivalMean, queues=queues))
        print(f'\n Running simulation with seed {self.seed}... \n')
        env.run(until=self.maxTime)
        print('\n Done \n')

    @staticmethod
    def NoInSystem(R):
        """Total numberJobs of Jobs in the resource R"""
        return len(R.put_queue) + len(R.users)

    @staticmethod
    def QueueSelector(d, counters):
        return random.sample(range(len(counters)), d)

    @property
    def RunSim(self):
        """
        Runs the simulation. Returns a dataframe if df is set to true.
        """
        self.__SimManager()
        if self.df:
            return pd.DataFrame(self.queuesOverTime)


class JSQSystem:
    """
    A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join for each arriving job.

    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param arrivalMean: Mean of Poisson arrival process.
    :param maxTime: Runtime limit.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param df: Whether or not a pandas.DataFrame of the queue sizes over time should be returned.
    :param d: Number of queues to parse.
    :param meanServer: Mean servicing time.
    :param doPrint: If true, each event will trigger a statement to be printed.

    Example
    -------
    .. code-block:: python

        # Specifies a SimPy environment consisting
        # of a JSQ-2 queueing system and a Poisson arrival process.
        sim = ParallelQueueSystem(arrivalMean=5, maxTime=100.0,
            parallelism=100, seed=1234, r=10, meanServer=1.0)
        sim.RunSim

    """

    def __init__(self, arrivalMean, maxTime, parallelism, seed, d, meanServer,  doPrint=False, df=False,
                 infiniteJobs=True, numberJobs=0):
        self.infiniteJobs = infiniteJobs
        self.d = d
        self.doPrint = doPrint
        self.timeInBank = meanServer
        self.seed = seed
        self.parallelism = parallelism
        self.maxTime = maxTime
        self.arrivalMean = arrivalMean
        self.Number = 0 if self.infiniteJobs else numberJobs
        self.queuesOverTime = []
        self.df = df

    def __SimManager(self):
        random.seed(self.seed)
        env = Environment()
        queues = {i: Resource(env) for i in range(self.parallelism)}

        env.process(PoissonArrivals(system=self, env=env, number=self.Number, interval=self.arrivalMean, queues=queues))
        print(f'\n Running simulation with seed {self.seed}... \n')
        env.run(until=self.maxTime)
        print('\n Done \n')

    @staticmethod
    def NoInSystem(R):
        """Total numberJobs of Jobs in the resource R"""
        return len(R.put_queue) + len(R.users)

    @staticmethod
    def QueueSelector(d, counters):
        return random.sample(range(len(counters)), d)

    @property
    def RunSim(self):
        """
        Runs the simulation. Returns a dataframe if df is set to true.
        """
        self.__SimManager()
        if self.df:
            return pd.DataFrame(self.queuesOverTime)
