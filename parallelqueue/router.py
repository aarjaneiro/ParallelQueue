import random


def DefaultRouter(job, system, env, name, queues, **kwargs):
    """Specifies the scheduling system used. If replication is enabled, this is the superclass for the set of each
    job and their replicas.

    :param job: Job process.
    :param system: System providing environment.
    :type system: base_models.ParallelQueueSystem
    :param env: Environment for the simulation.
    :type env: simpy.Environment
    :param name: Identifier for the job.
    :type name: str
    :param queues: A list of queues to consider.
    :type queues: List[simpy.Resource]
    """
    arrive = env.now
    parsed = {i: system.NoInSystem(queues[i]) for i in system.QueueSelector(system.d, system.parallelism, queues)}
    if system.MonitorHolder is not None:
        inputs = locals()
        for monitor in system.MonitorHolder.values():
            monitor.Add(inputs)

    if system.ReplicaDict is not None:  # Replication chosen
        choices = []
        if system.r:
            for i, value in parsed.items():
                if value <= system.r:
                    choices.append(i)  # the chosen queue numberJobs
        else:
            for i in parsed:
                choices.append(i)  # For no threshold
        if len(choices) < 1:
            choices = random.sample(list(parsed.keys()), 1)  # random choice
        if system.doPrint:
            print(f'{arrive:7.4f} {name}: Arrival for {len(choices)} copies')
        replicas = []
        for choice in choices:
            c = job(system, env, name, arrive, queues, choice, **kwargs)
            replicas.append(env.process(c))
        system.ReplicaDict[name] = replicas
        if system.MonitorHolder is not None:
            inputs = locals()
            for monitor in system.MonitorHolder.values():
                monitor.Add(inputs)
        yield from replicas  # Stronger than `for i in replicas: yield i` ∵ bijective
    else:  # Shortest queue case
        if system.doPrint:
            print(f'{arrive:7.4f} {name}: Arrival')
        choice = [k for k, v in sorted(parsed.items(), key=lambda item: item[1])][0]
        c = job(system, env, name, arrive, queues, choice, **kwargs)
        if system.MonitorHolder is not None:
            inputs = locals()
            for monitor in system.MonitorHolder.values():
                monitor.Add(inputs)
        env.process(c)
