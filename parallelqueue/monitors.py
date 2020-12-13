"""
This module contains methods for monitoring and visualization. As simulations run, the `Monitor` class interacts with
the main environment, gathering data at certain intervals. Moreover, the `Monitor` class was designed to be general enough
so that one can build their own by overriding its `Name` and its data-gathering `Add` function.
"""
from simpy import Process

try:
    from statsmodels.distributions import ECDF
except Exception:
    print(f"Warning, {Exception}")

from components import Job


class EmpiricalDistribution:
    def __init__(self, Y, t):
        """
        .. math::

            \\frac{1}{n} \\sum_{i=1}^{n}\\mathbb{1}_{X_{i} \\leq t}

        :param Y: The random variable (in this case, queues). Let Size(Y) = X as in the usual definition.
        :type Y: dict(Resource(Environment))
        :param t: The variable for which :math:`\\mathbb{1}_{X_{i} \\leq t}` is calculated across all X.
        :type t: float
        :return: :math:`x \\in [0,1]`
        :rtype: float

        """
        self.y = Y
        self.IList = [1 if (i.queue + i.users) <= t else 0 for i in self.y]

    def Calculate(self):
        return sum(self.IList) / len(self.IList)

    def sm_calculation(self, side='left'):
        """
        Using statsmodels.
        """
        return ECDF([i.queue + i.users for i in self.y], side)

    @property
    def I_List(self):
        """
        Returns the set of I's
        """
        return self.IList


# Base monitor class with overridable members.
class Monitor:
    def __init__(self):
        self.toData = []

    def Add(self, MonitorInputs: dict):
        return None

    @property
    def Data(self):
        return self.toData

    @property
    def Name(self):
        return None


class TimeQueueData(Monitor):

    def Add(self, MonitorInputs: dict):
        if "queues" in MonitorInputs:
            queues = MonitorInputs["queues"]
            self.toData.append({i: len(queues[i].put_queue) for i in range(len(queues))})

    @property
    def Name(self):
        return "TimeQueueData"


class ReplicaSets(Monitor):

    def Add(self, MonitorInputs: dict):
        if {"choices", "env"} <= MonitorInputs.keys():
            rep = MonitorInputs["choices"]
            time = MonitorInputs["env"].now
            self.toData.append({time: rep})

    @property
    def Name(self):
        return "ReplicaSets"
