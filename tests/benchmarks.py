import random
import time
import sys
import numpy as np
import parallelqueue.base_models as bm
import parallelqueue.monitors as mns


def JoinsReplicaClasses():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=1000, parallelism=100, seed=1234, d=5,
                                   doPrint=False,
                                   Replicas=True, Arrival=random.expovariate, AArgs=1,
                                   Service=random.expovariate, SArgs=0.5, Monitors=[mns.ReplicaClassCounts])

    model.RunSim()
    t2 = time.time()
    return t2 - t1


def TQSizes():
    t1 = time.time()
    model = bm.ParallelQueueSystem(maxTime=1000, parallelism=100, seed=1234, d=5,
                                   Replicas=False, Arrival=random.expovariate, AArgs=1,
                                   Service=random.expovariate, SArgs=0.5, Monitors=[mns.TimeQueueSize])

    model.RunSim()
    type(model.MonitorOutput)
    t2 = time.time()
    return t2 - t1


if __name__ == "__main__":
    print("Running Benchmark")
    JRC = [JoinsReplicaClasses() for i in range(30)]
    TQS = [TQSizes() for i in range(100)]
    print(f" JRC -- Mean: {np.mean(JRC)}, Var: {np.var(JRC)}")
    print(f" TQS -- Mean: {np.mean(TQS)}, Var: {np.var(TQS)}")
    print("Last run resulted in: \n")
    with open("priorbenchmark.txt", "r") as prev:
        print(prev.read())
    with open("priorbenchmark.txt", "w") as new:
        new.write(
f"""
Run on {sys.version} \n
JRC -- Mean: {np.mean(JRC)}, Var: {np.var(JRC)} \n
TQS -- Mean: {np.mean(TQS)}, Var: {np.var(TQS)}
"""
        )
