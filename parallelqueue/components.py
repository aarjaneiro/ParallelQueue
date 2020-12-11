"""
Basic building components (generators/processes) for parallel models. In general, the framework allows one to build
a model by defining an arrival, routing, and job/servicing process such that work is introduced in the order of
Arrivals->Router->Job/Servicing.
"""
#   TODO: Rewrite POI/EXP as implementations of the general functions Job/Arrivals

from simpy import Interrupt


def Job(doPrint, queuesOverTime, replicaDict, env, name, arrive, queues, choice, **kwargs):
    """For a redundancy model, this generator/process defines the behaviour of a job (replica or original) after routing.

    :param doPrint: If true, each event will trigger a statement to be printed.
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
    with queues[choice].request() as request:
        try:
            # Wait in queue
            Rename = f"{name}@{choice}"
            if doPrint:
                print(f'    ↳ {Rename}')
            yield request
            wait = env.now - arrive
            # at server
            if doPrint:
                print(f'{env.now:7.4f} {Rename}: Waited {wait:6.3f}')
            tib = kwargs["Service"](kwargs["SArgs"])
            yield env.timeout(tib)
            queuesOverTime.append({i: len(queues[i].put_queue) for i in range(len(queues))})
            if doPrint:
                print(f'{env.now:7.4f} {Rename}: Finished')
            if replicaDict is not None:
                for c in replicaDict[name]:
                    try:
                        c.interrupt()
                    except:
                        pass
        except Interrupt:
            if doPrint and Rename is not None:
                try:
                    print(f"    ↳ {Rename} - interrupted")  # This would be normal with replications
                except RuntimeError:
                    Exception(f"Job error for {queues[choice].request()}")
            else:
                Exception(f"Request error for {queues[choice].request()}")


def JobRouter(system, env, name, queues, **kwargs):
    """Specifies the scheduling system used. If replication is enabled, this is the superclass for the set of each job and their replicas.

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
    if system.ReplicaDict is not None:  # Replication chosen
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
            c = Job(system.doPrint, system.queuesOverTime, system.ReplicaDict, env, name, arrive, queues, choice,
                    **kwargs)

            replicas.append(env.process(c))
        system.ReplicaDict[name] = replicas  # Add a while statement?
        yield from replicas
    else:  # Shortest queue case
        if system.doPrint:
            print(f'{arrive:7.4f} {name}: Arrival')
        choices = [i for i in Q_length]
        choice = min(choices)
        c = Job(system.doPrint, system.queuesOverTime, None, env, name, arrive, queues, choice, **kwargs)
        env.process(c)


def Arrivals(system, env, number, queues, **kwargs):
    """General arrival process; interarrival times are defined by the given distribution

    :param system: System providing environment.
    :type system: parallelqueue.base_models.ParallelQueueSystem
    :param env: Environment for the simulation
    :type env: simpy.Environment
    :param number: Max numberJobs of jobs if infiniteJobs is false.
    :type number: int
    :param queues: A list of all queues making up the parallel system.
    :type queues: List[simpy.Resource]
    """
    if not system.infiniteJobs:
        for i in range(number):
            c = JobRouter(system, env, 'Job%02d' % (i + 1), queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)
    else:
        while True:  # referring to until not being passed
            number += 1
            c = JobRouter(system, env, 'Job%02d' % number, queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)
