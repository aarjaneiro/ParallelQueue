import random
from warnings import warn

import pandas as pd
from simpy import Environment, Resource

from parallelqueue.network import Network
from parallelqueue import monitors


class ParallelQueueSystem:
    """A queueing system wherein a Router chooses the smallest queue of d sampled (identical) queues to join,
    potentially replicating
    itself before enqueueing. For the sampled queues with sizes less than r, the job and/or its clones will join
    while awaiting
    service. After completing service, each job and its replicas are disposed of.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will override infiniteJobs if infiniteJobs is True.
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
    :param Monitors: Any monitor which overrides the methods of monitors.Monitor
    :param Network: Network class which defines the structure of the system.

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

    References
    ----------
    Heavy Traffic Analysis of the Mean Response Time for Load Balancing Policies in the Mean Field Regime
            Tim Hellemans, Benny Van Houdt (2020)
            https://arxiv.org/abs/2004.00876

    Redundancy-d:The Power of d Choices for Redundancy
            Kristen Gardner, Mor Harchol-Balter, Alan Scheller-Wolf,
            Mark Velednitsky, Samuel Zbarsky (2017)
            https://doi.org/10.1287/opre.2016.1582


    """

    def __init__(self, parallelism, seed, d, r=None, maxTime=None, doPrint=False, infiniteJobs=True, Replicas=True,
                 numberJobs=0, network=Network, **kwargs):
        self.network = network
        if infiniteJobs and numberJobs > 0:
            warn("\n Conflicting settings. Setting infiniteJobs := False, \n"
                 f"  Will generate {numberJobs} Job(s)!")
            self.infiniteJobs = False
        else:
            self.infiniteJobs = infiniteJobs
        self.d = d
        self.doPrint = doPrint
        self.seed = seed
        self.r = r
        self.parallelism = parallelism
        self.maxTime = maxTime
        self.ReplicaDict = {} if Replicas is True else None
        self.Number = 0 if self.infiniteJobs else numberJobs
        self.kwargs = kwargs
        self.MonitorHolder = {} if "Monitors" in self.kwargs is not None else None

        if self.MonitorHolder is not None:
            for monitor in self.kwargs["Monitors"]:
                m = monitor()  # initialize
                self.MonitorHolder[m.Name] = m

    def __SimManager(self):
        random.seed(self.seed)
        env = Environment()
        queues = {i: Resource(env, capacity=1) for i in range(self.parallelism)}
        env.process(self.network().Arrivals(system=self, env=env, number=self.Number, queues=queues, **self.kwargs))
        if self.doPrint:
            print(f"\n Running simulation with seed {self.seed}... \n")
        if self.maxTime is not None:
            env.run(until=self.maxTime)
        else:
            env.run()
        if self.doPrint:
            print("\n Done \n")

    def RunSim(self):
        """Runs the simulation."""
        self.__SimManager()

    @property
    def DataFrame(self):
        if "TimeQueueSize" in self.MonitorHolder:
            return pd.DataFrame(self.MonitorHolder["TimeQueueSize"].Data).transpose()
        else:
            raise Exception("Error: 'TimeQueueSize' must be monitored!")

    @property
    def MonitorOutput(self):
        return {name: monitor.Data for name, monitor in self.MonitorHolder.items()}


# New 0.0.5 - Base models rewritten with same base class
def RedundancyQueueSystem(parallelism, seed, d, Arrival, AArgs, Service, SArgs, Monitors=[monitors.TimeQueueSize],
                          r=None, maxTime=None, doPrint=False, infiniteJobs=True, numberJobs=0):
    """A queueing system wherein a Router chooses the smallest queue of d sampled (identical) queues to join,
    potentially replicating
    itself before enqueueing. For the sampled queues with sizes less than r, the job and/or its clones will join
    while awaiting
    service. After completing service, each job and its replicas are disposed of.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param d: Number of queues to parse.
    :param doPrint: If true, each event will trigger a statement to be printed.
    :param Arrival: A kwarg specifying the arrival distribution to use (a function).
    :param AArgs: parameters needed by the function.
    :param Service: A kwarg specifying the service distribution to use (a function).
    :param SArgs: parameters needed by the function.
    :param Monitors: Any monitor which overrides the methods of monitors.Monitor
    :type Monitors: monitors.Monitor

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
    kwargs = {
        "Arrival": Arrival, "AArgs": AArgs, "Service": Service, "SArgs": SArgs, "Monitors": Monitors,
    }  # Pack to use as argument
    return ParallelQueueSystem(parallelism=parallelism, seed=seed, d=d, r=r, maxTime=maxTime, doPrint=doPrint,
                               infiniteJobs=infiniteJobs, numberJobs=numberJobs, Replicas=True, **kwargs)


def JSQd(parallelism, seed, d, Arrival, AArgs, Service, SArgs, Monitors=[monitors.TimeQueueSize], r=None, maxTime=None,
         doPrint=False, infiniteJobs=True, numberJobs=0):
    """A queueing system wherein a Router chooses the smallest queue of d sampled (identical) queues to join for
    each arriving job.

    :param maxTime: If set, becomes the maximum allotted time for this simulation.
    :param numberJobs: Max number of jobs if infiniteJobs is False. Will be ignored if infiniteJobs is True.
    :param parallelism: Number of queues in parallel.
    :param seed: Random number generation seed.
    :param r: Threshold. Should be set to an integer, defaulting to :code:`None` otherwise.
    :param infiniteJobs: If true, there will be no upper limit for the number of jobs generated.
    :param d: Number of queues to parse.
    :param doPrint: If true, each event will trigger a statement to be printed.
    :param Arrival: A kwarg specifying the arrival distribution to use (a function).
    :param AArgs: parameters needed by the function.
    :param Service: A kwarg specifying the service distribution to use (a function).
    :param SArgs: parameters needed by the function.
    :param Monitors: Any monitor which overrides the methods of monitors.Monitor
    :type Monitors: monitors.Monitor
    """
    kwargs = {
        "Arrival": Arrival, "AArgs": AArgs, "Service": Service, "SArgs": SArgs, "Monitors": Monitors
    }  # Pack to use as argument
    return ParallelQueueSystem(parallelism=parallelism, seed=seed, d=d, r=r, maxTime=maxTime, doPrint=doPrint,
                               infiniteJobs=infiniteJobs, numberJobs=numberJobs, Replicas=False, **kwargs)
