import random
import time

import numpy as np

import parallelqueue.base_models as bm
import parallelqueue.monitors as mns


def JoinsReplicaClasses():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                            Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                            Service=random.expovariate, SArgs=1, Monitors=[mns.ReplicaClassCounts])

    model.RunSim()
    t2 = time.time()
    return t2 - t1


def TQSizes():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                            Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                            Service=random.expovariate, SArgs=1, Monitors=[mns.TimeQueueSize])

    model.RunSim()
    t2 = time.time()
    return t2 - t1


if __name__ == "__main__":
    JRC = [JoinsReplicaClasses() for i in range(100)]
    TQS = [TQSizes() for i in range(100)]
    print(f" JRC -- Mean: {np.mean(JRC)}, Var: {np.var(JRC)}")
    print(f" TQS -- Mean: {np.mean(TQS)}, Var: {np.var(TQS)}")

# January 12, 2021:
# JRC -- Mean: 0.010729830265045166, Var: 4.112422304166899e-05
# TQS -- Mean: 0.03033794164657593, Var: 9.088805604662299e-05
