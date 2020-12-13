"""
This module contains methods for monitoring and visualization. As simulations run, the `Monitor` class interacts with
the main environment, gathering data at certain intervals. Moreover, the `Monitor` class was designed to be general
enough
so that one can build their own by overriding its `Name` and its data-gathering `Add` function.
"""

try:
    from statsmodels.distributions import ECDF
except:
    print(f"Warning, EmpiricalDistribution.sm_calculation requires `statsmodels`")


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

    def sm_calculation(self, side="left"):
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
        self.toData = {}

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
        if {"env", "queues"} <= MonitorInputs.keys():  # Leaving system
            queues = MonitorInputs["queues"]
            self.toData[MonitorInputs["env"].now] = {i: len(queues[i].put_queue) for i in range(len(queues))}

    @property
    def Name(self):
        return "TimeQueueData"


class ReplicaSets(Monitor):
    def Add(self, MonitorInputs: dict):
        if {"choices", "env", "name"} <= MonitorInputs.keys():
            time = MonitorInputs["env"].now
            name = MonitorInputs["name"]
            self.toData[name] = {"choices": MonitorInputs["choices"], "entry": time}

        elif {"env", "name"} <= MonitorInputs.keys():  # Leaving system
            time = MonitorInputs["env"].now
            name = MonitorInputs["name"]
            if name in self.toData.keys():
                self.toData[name]["exit"] = time

    @property
    def Name(self):
        return "ReplicaSets"


class JobTime(Monitor):
    def __init__(self):
        super().__init__()
        self.dataHelper = {}

    def Add(self, MonitorInputs: dict):
        if {"choices", "env", "name", } <= MonitorInputs.keys():  # Choices is dummy to ensure at router
            time = MonitorInputs["env"].now
            name = MonitorInputs["name"]
            self.dataHelper[name] = time

        elif {"env", "name"} <= MonitorInputs.keys():  # Leaving system
            time = MonitorInputs["env"].now
            name = MonitorInputs["name"]
            if name in self.dataHelper.keys():
                self.toData[name] = time - self.dataHelper[name]
                self.dataHelper.pop(name)  # Clear space

    @property
    def Name(self):
        return "ReplicaSets"
