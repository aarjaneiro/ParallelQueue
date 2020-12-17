"""
Basic building components (generators/processes) for parallel models. In general, the framework allows one to build
a model by defining an arrival, routing, and job/servicing process such that work is introduced in the order of
Arrivals->Router->Job/Servicing.
"""
from parallelqueue.arrivals import DefaultArrivals
from parallelqueue.jobs import DefaultJob
from parallelqueue.routers import DefaultRouter


class Network:
    """
    The Network constructor allows a user to create a queueing network by overriding each member.
    Upon generation, jobs flow through a network in the order of: Arrivals → Router → Job. By default, the Network class
    can be used to handle JSQd, Redundancy-d, and Threshold-(d,r) models.
    """

    def __init__(self, **kwargs):
        self.network_args = {}  # Allow user to pass anything they deem fit.
        for k, v in kwargs.items():
            self.network_args[k] = v

    @staticmethod
    def Job(system, env, name, arrive, queues, choice, **kwargs):
        return DefaultJob(system, env, name, arrive, queues, choice, **kwargs)

    def Router(self, system, env, name, queues, **kwargs):
        return DefaultRouter(self.Job, system, env, name, queues, **kwargs)

    def Arrivals(self, system, env, number, queues, **kwargs):
        return DefaultArrivals(self.Router, system, env, number, queues, **kwargs)
