"""
For use with a profiling system.
"""
import random
import parallelqueue.base_models as bm
import parallelqueue.monitors as mns


def RunsReplicaClasses(time=10000):
    model = bm.ParallelQueueSystem(maxTime=time, parallelism=5, seed=1234, d=5,
                                   doPrint=False,
                                   Replicas=True, Arrival=random.expovariate, AArgs=10,
                                   Service=random.expovariate, SArgs=0.5, Monitors=[mns.TimeQueueSize])

    model.RunSim()
    return model.DataFrame


if __name__ == "__main__":
    print("Running Benchmark")
    RunsReplicaClasses()
