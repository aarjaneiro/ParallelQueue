from simpy import Interrupt


def DefaultJob(system, env, name, arrive, queues, choice, **kwargs):
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
