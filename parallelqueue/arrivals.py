def DefaultArrivals(router, system, env, number, queues, **kwargs):
    """General arrival process; interarrival times are defined by the given distribution

    :param router: Router process.
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
            c = router(system, env, 'Job%02d' % (i + 1), queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)
    else:
        while True:  # referring to until not being passed
            number += 1
            c = router(system, env, 'Job%02d' % number, queues, **kwargs)
            env.process(c)
            t = kwargs["Arrival"](kwargs["AArgs"])
            yield env.timeout(t)


