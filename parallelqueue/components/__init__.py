"""
Basic building components (generators/processes) for parallel models.
"""

import random

from simpy import Interrupt


def Replica(doPrint, meanServer, queuesOverTime, replicaDict, env, name, arrive, queues, choice):
    """
    For a redundancy model, this generator/process defines the behaviour of a job (replica or original) as they await their turn.

    :param doPrint: If true, each event will trigger a statement to be printed.
    :param meanServer: Mean servicing time.
    :param queuesOverTime: A set of queues passed by the simulation manager representing the time-evolution of the system.
    :type queuesOverTime: List[simpy.Resource]
    :param replicaDict: A set of a job and its replications, of which this generator itself is a member of.
    :type replicaDict: {str: List[simpy.Process]}
    :param env: Environment for the simulation
    :type env: simpy.Environment
    :param name: Identifier for the job.
    :type name: str
    :param queues: A list of queuesOverTime.
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
                if doPrint:
                    print(f'{env.now:7.4f} {Rename}: Waited {wait:6.3f}')
                tib = random.expovariate(1.0 / meanServer)
                yield env.timeout(tib)
                queuesOverTime.append({i: len(queues[i].put_queue) for i in range(len(queues))})
                if doPrint:
                    print(f'{env.now:7.4f} {Rename}: Finished')
                for c in replicaDict[name]:
                    try:
                        c.interrupt()
                    except:
                        pass
        except Interrupt:
            if doPrint:
                print(f'{Rename} - interrupted')


def Source(system, env, number, interval, queues):
    """
    Poisson arrival process.

    :param system: System providing environment.
    :type system: parallelqueue.base_models.ParallelQueueSystem
    :param env: Environment for the simulation
    :type env: simpy.Environment
    :param number: Max numberJobs of jobs if infiniteJobs is false.
    :type number: int
    :param interval: Poisson rate parameter :math:`\lambda`.
    :type interval: float
    :param queues: A list of all queues making up the parallel system.
    :type queues: List[simpy.Resource]
    """
    if not system.infiniteJobs:
        for i in range(number):
            c = Job(system, env, 'Job%02d' % i, queues)
            env.process(c)
            t = random.expovariate(1.0 / interval)
            yield env.timeout(t)
    else:
        while True:  # referring to until not being passed
            i = number
            number += 1
            c = Job(system, env, 'Job%02d' % i, queues)
            env.process(c)
            t = random.expovariate(1.0 / interval)
            yield env.timeout(t)


def Job(system, env, name, queues):
    """
    Specifies a job in the system. If replication is enabled, this is the superclass for the set of each job and their replicas.

    :param system: System providing environment.
    :type system: parallelqueue.base_models.ParallelQueueSystem
    :param env: Environment for the simulation.
    :type env: simpy.Environment
    :param name: Identifier for the job.
    :type name: str
    :param queues: A list of queues to consider.
    :type queues: List[simpy.Resource]
    """
    arrive = env.now
    Q_length = {i: system.NoInSystem(queues[i]) for i in system.QueueSelector(system.d, queues)}
    system.queuesOverTime.append({i: len(queues[i].put_queue) for i in range(len(queues))})
    choices = []
    if system.r:
        for i, value in Q_length.items():
            if value <= system.r:
                choices.append(i)  # the chosen queue numberJobs
    else:
        for i in Q_length:
            choices.append(i)  # For no threshold
    if len(choices) < 1:
        choices = [list(Q_length.keys())[0]]  # random choice
    if system.doPrint:
        print(f'{arrive:7.4f} {name}: Arrival for {len(choices)} copies')
    replicas = []
    for choice in choices:
        c = Replica(system.doPrint, system.timeInBank, system.queuesOverTime, system.ReplicaDict, env, name, arrive,
                    queues,
                    choice)
        replicas.append(env.process(c))
    system.ReplicaDict[name] = replicas  # Add a while statement?
    yield from replicas
