"""
Basic building components (generators/processes) for parallel models. In general, the framework allows one to build
a model by defining an arrival, routing, and job/servicing process such that work is introduced in the order of
Arrivals->Router->Job/Servicing.
"""
#   TODO: Components → Classes with overridable segments corresponding to current Monitor checks

import random

from simpy import Interrupt


def Job(system, env, name, arrive, queues, choice, **kwargs):
    """For a redundancy model, this generator/process defines the behaviour of a job (replica or original) after
    routing.

    :param system: System providing environment.
    :type system: base_models.ParallelQueueSystem
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
            if system.doPrint:
                print(f'    ↳ {Rename}')
            yield request
            wait = env.now - arrive
            # at server ⇒ Next job waits until finished.
            if system.doPrint:
                print(f'{env.now:7.4f} {Rename}: Waited {wait:6.3f}')
            tib = kwargs["Service"](kwargs["SArgs"])
            yield env.timeout(tib)
            finish = env.now - arrive
            if system.doPrint:
                print(f'{env.now:7.4f} {Rename}: Finished — Total {finish:2.3f}')
            if system.ReplicaDict is not None:
                for c in system.ReplicaDict[name]:
                    try:
                        c.interrupt()
                    except:
                        pass
            if system.MonitorHolder is not None:
                inputs = locals()
                for monitor in system.MonitorHolder.values():
                    monitor.Add(inputs)
        except Interrupt:
            if Rename is not None:
                try:  # similar: simpy/examples/machine_shop
                    if system.doPrint:
                        print(f"    ↳ {Rename} - Interrupted")  # This would be normal with replications
                except RuntimeError:
                    Exception(f"Job error for {queues[choice].request()}")
            else:
                Exception(f"Request error for {queues[choice].request()}")


def Router(system, env, name, queues, **kwargs):
    """Specifies the scheduling system used. If replication is enabled, this is the superclass for the set of each
    job and their replicas.

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
            c = Job(system, env, name, arrive, queues, choice, **kwargs)
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
        c = Job(system, env, name, arrive, queues, choice, **kwargs)
        if system.MonitorHolder is not None:
            inputs = locals()
            for monitor in system.MonitorHolder.values():
                monitor.Add(inputs)
        env.process(c)


def Arrivals(system, env, number, queues, **kwargs):
    """General arrival process; interarrival times are defined by the given distribution

    :param system: System providing environment.
    :type system: base_models.ParallelQueueSystem
    :param env: Environment for the simulation
    :type env: simpy.Environment
    :param number: Max numberJobs of jobs if infiniteJobs is false.
    :type number: int
    :param queues: A list of all queues making up the parallel system.
    :type queues: List[simpy.Resource]
    """
    if not system.infiniteJobs:
        for i in range(number):
            c = Router(system, env, 'Job%02d' % (i + 1), queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)
    else:
        while True:  # referring to until not being passed
            number += 1
            c = Router(system, env, 'Job%02d' % number, queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)
