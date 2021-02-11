import random
import time

import numpy as np

import parallelqueue.base_models as bm
import parallelqueue.monitors as mns


def JoinsReplicaClasses():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=100, parallelism=1000, seed=1234, d=2,
                                   doPrint=True,
                                   Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                   Service=random.expovariate, SArgs=1, Monitors=[mns.ReplicaClassCounts])

    model.RunSim()
    t2 = time.time()
    return t2 - t1


def TQSizes():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=100, parallelism=1000, seed=1234, d=2,
                                   Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                   Service=random.expovariate, SArgs=1, Monitors=[mns.TimeQueueSize])

    model.RunSim()
    type(model.MonitorOutput)
    t2 = time.time()
    return t2 - t1


if __name__ == "__main__":
    JRC = [JoinsReplicaClasses() for i in range(30)]
    TQS = [TQSizes() for i in range(100)]
    print(f" JRC -- Mean: {np.mean(JRC)}, Var: {np.var(JRC)}")
    print(f" TQS -- Mean: {np.mean(TQS)}, Var: {np.var(TQS)}")

# January 13, 2021:
# JRC - - Mean: 0.01253662109375, Var: 9.744768944453125e-05
# TQS - - Mean: 0.03323680400848389, Var: 0.00013722097561937976

# model.MonitorHolder["ReplicaClassCounts"].toData
# data = model.MonitorHolder["ReplicaClassCounts"].toData
