import random

import pandas as pd
from simpy import Environment, Resource

from parallelqueue.components import PoissonArrivals, GeneralArrivals


class ParallelQueueSystem:
    """A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join, potentially replicating
    itself before enqueueing. For the sampled queues with sizes less than r, the job and/or its clones will join while awaiting
    service. After completing service, each job and its replicas are disposed of.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param df: Whether or not a pandas.DataFrame of the queue sizes over time should be returned.
    :param d: Number of queues to parse.
    :param doPrint: If true, each event will trigger a statement to be printed.
    :param Arrival: A kwarg specifying the arrival distribution to use (a function).
    :param AArgs: parameters needed by the function.
    :param Service: A kwarg specifying the service distribution to use (a function).
    :param SArgs: parameters needed by the function.

    Example
    -------
    .. code-block:: python

        # Specifies a SimPy environment consisting
        # of a Redundancy-2 queueing system and a Poisson arrival process.
        sim = ParallelQueueSystem(maxTime=100.0,
            parallelism=100, seed=1234, d=2, Replicas=True,
            Arrival=random.expovariate, AArgs=0.5,
            Service=random.expovariate, SArgs=1)
        sim.RunSim()

    """

    def __init__(self, parallelism, seed, d, r=None, maxTime=None, doPrint=False, df=False,
                 infiniteJobs=True, Replicas=True, numberJobs=0, **kwargs):
        if infiniteJobs and numberJobs > 1:
            Exception("ERROR: A limit to jobs has been set while assuming infinite jobs!")
        self.infiniteJobs = infiniteJobs
        self.d = d
        self.doPrint = doPrint
        self.seed = seed
        self.r = r
        self.parallelism = parallelism
        self.maxTime = maxTime
        self.ReplicaDict = {} if Replicas is True else None
        self.Number = 0 if self.infiniteJobs else numberJobs
        self.queuesOverTime = []
        self.df = df
        self.kwargs = kwargs

    def __SimManager(self):
        random.seed(self.seed)
        env = Environment()
        queues = {i: Resource(env, capacity=1) for i in range(self.parallelism)}

        env.process(GeneralArrivals(system=self, env=env, number=self.Number,
                                    queues=queues, **self.kwargs))
        print(f'\n Running simulation with seed {self.seed}... \n')
        if self.maxTime is not None:
            env.run(until=self.maxTime)
        else:
            env.run()
        print('\n Done \n')

    def RunSim(self):
        """Runs the simulation."""
        self.__SimManager()

    @staticmethod
    def NoInSystem(R):
        """Total numberJobs of Jobs in the resource R"""
        return len(R.put_queue) + len(R.users)

    @staticmethod
    def QueueSelector(d, counters):
        return random.sample(range(len(counters)), d)

    @property
    def DataFrame(self):
        if self.df:
            return pd.DataFrame(self.queuesOverTime)


# New 0.0.5 - Base models rewritten with same base class
def RedundancyQueueSystem(parallelism, seed, d, Arrival, AArgs, Service, SArgs, r=None, maxTime=None, doPrint=False,
                          df=False, infiniteJobs=True, numberJobs=0):
    """A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join, potentially replicating
    itself before enqueueing. For the sampled queues with sizes less than r, the job and/or its clones will join while awaiting
    service. After completing service, each job and its replicas are disposed of.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param df: Whether or not a pandas.DataFrame of the queue sizes over time should be returned.
    :param d: Number of queues to parse.
    :param doPrint: If true, each event will trigger a statement to be printed.
    :param Arrival: A kwarg specifying the arrival distribution to use (a function).
    :param AArgs: parameters needed by the function.
    :param Service: A kwarg specifying the service distribution to use (a function).
    :param SArgs: parameters needed by the function.

    Example
    -------
    .. code-block:: python

        # Specifies a SimPy environment consisting
        # of a Redundancy-2 queueing system and a Poisson arrival process.
        sim = RedundancyQueueSystem(maxTime=100.0,
            parallelism=100, seed=1234, d=2,
            Arrival=random.expovariate, AArgs=0.5,
            Service=random.expovariate, SArgs=1)
        sim.RunSim()

    """
    kwargs = {"Arrival": Arrival, "AArgs": AArgs, "Service": Service, "SArgs": SArgs}  # Pack to use as argument
    return ParallelQueueSystem(parallelism=parallelism, seed=seed, d=d, r=r, maxTime=maxTime, doPrint=doPrint,
                               df=df, infiniteJobs=infiniteJobs, numberJobs=numberJobs, Replicas=True, **kwargs)


def JSQd(parallelism, seed, d, Arrival, AArgs, Service, SArgs, r=None, maxTime=None, doPrint=False,
         df=False, infiniteJobs=True, numberJobs=0):
    """A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join for each arriving job.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param df: Whether or not a pandas.DataFrame of the queue sizes over time should be returned.
    :param d: Number of queues to parse.
    :param doPrint: If true, each event will trigger a statement to be printed.
    :param Arrival: A kwarg specifying the arrival distribution to use (a function).
    :param AArgs: parameters needed by the function.
    :param Service: A kwarg specifying the service distribution to use (a function).
    :param SArgs: parameters needed by the function.
    """
    kwargs = {"Arrival": Arrival, "AArgs": AArgs, "Service": Service, "SArgs": SArgs}  # Pack to use as argument
    return ParallelQueueSystem(parallelism=parallelism, seed=seed, d=d, r=r, maxTime=maxTime, doPrint=doPrint,
                               df=df, infiniteJobs=infiniteJobs, numberJobs=numberJobs, Replicas=False, **kwargs)


# To depreciate.
class OldJSQSystem:
    """A queueing system wherein a JobRouter chooses the smallest queue of d sampled (identical) queues to join for each arriving job.

    .. warning::
       DEPRECIATION WARNING: This implementation will be removed!

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
        sim = RedundancyQueueSystem(arrivalMean=5, maxTime=100.0,
            parallelism=100, seed=1234, r=10, meanServer=1.0)
        sim.RunSim()

    """

    def __init__(self, arrivalMean, maxTime, parallelism, seed, d, meanServer, doPrint=False, df=False,
                 infiniteJobs=True, numberJobs=0, **kwargs):
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
        """Runs the simulation. Returns a dataframe if df is set to true."""
        self.__SimManager()
        if self.df:
            return pd.DataFrame(self.queuesOverTime)
