import random
import pandas as pd
from simpy import Environment, Resource, Interrupt


class ParallelQueueSystem:
    """
    A queueing system wherein a Job chooses the smallest queue of d sampled (identical) queues to join, potentially replicating
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
            parallelism=100, seed=1234, r=10, d=2, meanServer=1.0)
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
        self.Queues = []
        self.df = df

    def Source(self, env, number, interval, queues):
        """
        Poisson arrival process.

        :param env: Environment for the simulation
        :type env: simpy.Environment
        :param number: Max numberJobs of jobs if infiniteJobs is false.
        :type number: int
        :param interval: Poisson rate parameter :math:`\lambda`.
        :type interval: float
        :param queues: A list of all queues making up the parallel system.
        :type queues: List[simpy.Resource]
        """
        if not self.infiniteJobs:
            for i in range(number):
                c = self.Job(env, 'Job%02d' % i, queues)
                env.process(c)
                t = random.expovariate(1.0 / interval)
                yield env.timeout(t)
        else:
            while True:  # referring to until not being passed
                i = number
                number += 1
                c = self.Job(env, 'Job%02d' % i, queues)
                env.process(c)
                t = random.expovariate(1.0 / interval)
                yield env.timeout(t)

    def __SimManager(self):
        random.seed(self.seed)
        env = Environment()
        queues = {i: Resource(env) for i in range(self.parallelism)}
        env.process(self.Source(env, self.Number, self.arrivalMean, queues))
        print(f'\n Running simulation with seed {self.seed}... \n')
        env.run(until=self.maxTime)
        print('\n Done \n')

    def Job(self, env, name, queues):
        """
        Specifies a job in the system. If replication is enabled, this is the superclass for the set of each job and their replicas.

        :param env: Environment for the simulation
        :type env: simpy.Environment
        :param name: Identifier for the job.
        :type name: str
        :param queues: A list of Queues
        :type queues: List[simpy.Resource]
        """
        arrive = env.now
        Q_length = {i: self.NoInSystem(queues[i]) for i in self.QueueSelector(self.d, queues)}
        self.Queues.append({i: len(queues[i].put_queue) for i in range(len(queues))})
        choices = []
        if self.r:
            for i, value in Q_length.items():
                if value <= self.r:
                    choices.append(i)  # the chosen queue numberJobs
        else:
            for i in Q_length:
                choices.append(i)  # For no threshold
        if len(choices) < 1:
            choices = [list(Q_length.keys())[0]]  # random choice
        if self.doPrint:
            print(f'{arrive:7.4f} {name}: Arrival for {len(choices)} copies')
        replicas = []
        for choice in choices:
            c = self.Replica(env, name, arrive, queues, choice)
            replicas.append(env.process(c))
        self.ReplicaDict[name] = replicas  # Add a while statement?
        yield from replicas

    def Replica(self, env, name, arrive, queues, choice):
        """
        For a redundancy model, this generator/process defines the behaviour of a job (replica or original) as they await their turn.
        
        :param env: Environment for the simulation
        :type env: simpy.Environment
        :param name: Identifier for the job.
        :type name: str
        :param queues: A list of Queues.
        :type queues: List[simpy.Resource]
        :param arrive: Time of job arrival (before replication).
        :type arrive: float
        :param choice: The queue which this replica is currently in
        :type choice: int
        """
        while True:
            try:
                with queues[choice].request() as request:
                    # Wait in queue
                    Rename = f"{name}: {choice}"
                    yield request
                    wait = env.now - arrive
                    # at server
                    if self.doPrint:
                        print(f'{env.now:7.4f} {Rename}: Waited {wait:6.3f}')
                    tib = random.expovariate(1.0 / self.timeInBank)
                    yield env.timeout(tib)
                    self.Queues.append({i: len(queues[i].put_queue) for i in range(len(queues))})
                    if self.doPrint:
                        print(f'{env.now:7.4f} {Rename}: Finished')
                    for c in self.ReplicaDict[name]:
                        try:
                            c.interrupt()
                        except:
                            pass
            except Interrupt:
                if self.doPrint:
                    print(f'{Rename} - interrupted')

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
            return pd.DataFrame(self.Queues)
