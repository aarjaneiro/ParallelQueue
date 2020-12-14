"""
This module contains methods for monitoring and visualization. As simulations run, the `Monitor` class interacts with
the main environment, gathering data at certain intervals. Moreover, the `Monitor` class was designed to be general
enough
so that one can build their own by overriding its `Name` and its data-gathering `Add` function.
"""


#   TODO: Introduce analysis class which can interact with Monitor interface

# Base monitor class with overridable members.
class Monitor:
    """
    Base class defining the behaviour of monitors over `ParallelQueue` models.
    Unless overridden, the return of this class will be a `dict` of values.

    Note
    ----
    In general, if you need data not provided by any one of the default implementations,
    you would fare better by overriding elements of `Monitor` as needed. This is as
    opposed to calling a collection of monitors which will then need to update frequently.
    """

    def __init__(self):
        self.toData = {}

    def Add(self, MonitorInputs: dict):
        return None

    @property
    def Data(self):
        return self.toData

    @property
    def Name(self):
        return None


class TimeQueueSize(Monitor):
    """
    Tracks queue sizes over time.
    """

    def Add(self, MonitorInputs: dict):  # Env always exists
        if {"queues"} <= MonitorInputs.keys():  # Leaving system
            queues = MonitorInputs["queues"]
            self.toData[MonitorInputs["env"].now] = {i: len(queues[i].put_queue) for i in range(len(queues))}

    @property
    def Name(self):
        return "TimeQueueSize"


class ReplicaSets(Monitor):
    """
    Tracks replica sets generated over time, along with their times of creation and disposal.
    """

    def Add(self, MonitorInputs: dict):
        if {"choices", "name"} <= MonitorInputs.keys():
            time = MonitorInputs["env"].now  # Env always exists
            name = MonitorInputs["name"]
            self.toData[name] = {"choices": MonitorInputs["choices"], "entry": time}

        elif {"name"} <= MonitorInputs.keys():  # Leaving system
            time = MonitorInputs["env"].now
            name = MonitorInputs["name"]
            if name in self.toData.keys():
                self.toData[name]["exit"] = time

    @property
    def Name(self):
        return "ReplicaSets"


class JobTime(Monitor):
    """
    Tracks time of job entry and exit.
    """

    def Add(self, MonitorInputs: dict):
        if {"arrive", "wait", "name"} <= MonitorInputs.keys():  # `wait` is a dummy to know @ server
            name = MonitorInputs["name"]
            self.toData[name] = {"entry": MonitorInputs["arrive"], "exit": MonitorInputs["env"].now}

    @property
    def Name(self):
        return "JobTime"


class JobTotal(Monitor):
    """
    Tracks total time each job/set spends in system.
    To get the mean time each job/set spends:

    Example
    -------

    .. code-block:: python

        from monitors import JobTotal
        import pandas as pd
        sim = base_models.RedundancyQueueSystem(maxTime=100.0, parallelism=10, seed=1234, d=2, Arrival=random.expovariate,
                                      AArgs=0.5, Service=random.expovariate, SArgs=0.2, doPrint=True, Monitors = [JobTotal])
        sim.RunSim()
        totals = sim.MonitorOutput["JobTotal"]
        mean = pd.Series(totals, index = totals.keys()).mean()

    """

    def Add(self, MonitorInputs: dict):
        if {"finish", "name"} <= MonitorInputs.keys():
            name = MonitorInputs["name"]
            self.toData[name] = MonitorInputs["finish"]

    @property
    def Name(self):
        return "JobTotal"
