#cython: language_level=3

"""
This module contains methods for monitoring and visualization. As simulations run, the `Monitor` class interacts with
the main environment, gathering data at certain intervals. Moreover, the `Monitor` class was designed to be general
enough
so that one can build their own by overriding its `Name` and its data-gathering `Add` function.
"""
from collections import deque
from typing import Set

import pandas as pd
import numpy as np
cimport numpy as np

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
    def Data(self) -> dict:
        return self.toData

    @property
    def Name(self) -> str:
        return ""


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


#TODO: Remove dependence on pandas & speed up the per set search
class ReplicaClassCounts(Monitor):  # "super" init can be added for perset usage
    def Add(self, MonitorInputs: dict):
        if {"choices", "name"} <= MonitorInputs.keys():
            time = np.float32(MonitorInputs["env"].now)  # Env always exists
            name = MonitorInputs["name"]
            choices: list = MonitorInputs["choices"]
            self.toData[name] = {"choices": frozenset(choices), "entry": time}

        elif {"name"} <= MonitorInputs.keys():  # Leaving system
            time = np.float32(MonitorInputs["env"].now)
            name = MonitorInputs["name"]
            if name in self.toData.keys():
                self.toData[name]["exit"] = time

    @property
    def Data(self):
        # basedata = {f"{value['choices']}@{key}": value for key, value in self.toData.items()}
        data = pd.DataFrame(self.toData).transpose()
        events = deque(sorted(set(data["entry"].to_list()).union(
            set(data["exit"].to_list()))))  # set => drop repeats, sorted makes low->high, deque => drop hash table
        ret = {}
        while events:
            current = events.popleft()
            parse = data[data["exit"] >= current]  # Restrict to upper bounds
            loc: pd.DataFrame = __perSet__(parse[parse["entry"] <= current]).groupby("choices").count()["entry"]
            ret[current] = loc
        return ret

    @property
    def Name(self):
        return "ReplicaClassCounts"


cdef __perSet__(df: pd.DataFrame): # auto-like method
    """
    Joins frozensets with at least one common element.
    """
    cdef set memory = set()
    cdef frozenset frozen, localFrozen, others
    cdef int i
    cdef set categories = set(df["choices"])  # gets uniques
    for frozen in categories:  # for frozen set
        localFrozen = frozen  # copies without changing values in iteration below
        for i in frozen:
            if i not in memory:  # member not done before
                memory.add(i)  # only to do once
                for others in df["choices"]:  # changed from list comprehension
                    if others != localFrozen and i in others:  # skip if equal or doesnt contain i
                        together = localFrozen.union(others)  # value to reassign in df for old frozen/others
                        for change in df.index[df["choices"] == localFrozen].tolist():
                            df.at[change, "choices"] = together
                        for change in df.index[df["choices"] == others].tolist():
                            df.at[change, "choices"] = together
                        localFrozen = together  # these have now been done for i
    return df