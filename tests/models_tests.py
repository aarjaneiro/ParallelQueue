try:
    import pytest
except:
    print("Warning: Please install pytest to run all tests at once without needing to manually specify tests \n")
import parallelqueue
import random
import io
from contextlib import redirect_stdout
from pure_simpy import SimTest


def test_seed():
    # 1 seed should give 1 result across 2 initializations
    base = 0
    sim1 = parallelqueue.base_models.ParallelQueueSystem(df=True, maxTime=100.0, parallelism=100, seed=1234, d=2,
                                                         Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                                         Service=random.expovariate, SArgs=1)
    sim1.RunSim()
    df1 = sim1.DataFrame
    sim2 = parallelqueue.base_models.ParallelQueueSystem(df=True, maxTime=100.0, parallelism=100, seed=1234, d=2,
                                                         Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                                         Service=random.expovariate, SArgs=1)
    sim2.RunSim()
    df2 = sim2.DataFrame
    for i in range(df1.shape[0]):
        for j in range(df1.shape[1]):
            if df1.iloc[i, j] != df2.iloc[i, j]:
                base += 1
    assert base == 0


def test_runAll():
    # Tries all base models
    base = 0
    sims = [parallelqueue.base_models.ParallelQueueSystem(df=True, maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                                          Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                                          Service=random.expovariate, SArgs=1),
            parallelqueue.base_models.JSQd(df=True, maxTime=100.0, parallelism=1000, seed=1234,
                                           d=2, Arrival=random.expovariate, AArgs=0.5,
                                           Service=random.expovariate, SArgs=1),
            parallelqueue.base_models.RedundancyQueueSystem(df=True, maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                                            Arrival=random.expovariate, AArgs=0.5,
                                                            Service=random.expovariate, SArgs=1)]
    for i in sims:
        try:
            i.RunSim()
        except RuntimeError:
            base += 1
    assert base == 0


def simpy_test():
    sim = parallelqueue.base_models.JSQd(df=True, numberJobs=5, infiniteJobs=False, parallelism=2, seed=12345,
                                         d=2, Arrival=random.expovariate, AArgs=1,
                                         Service=random.expovariate, SArgs=1 / 10, doPrint=True)

    f = io.StringIO()
    with redirect_stdout(f):
        sim.RunSim()
    ls = f.getvalue().split(" ")
    test = []
    for i in ls:
        try:
            test.append(float(i))
        except:
            pass
    original = SimTest()
    print(f"simpy_test result: Expect True, got {original == test}")
    assert original == test
