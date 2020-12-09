try:
    import pytest
except:
    print("Warning: Please install pytest to run all tests at once without needing to manually specify tests \n")
import parallelqueue
import random


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

# def test_bank():
#     pq = parallelqueue.base_models.RedundancyQueueSystem(df=True, parallelism=1, seed=42,
#                                         d=1, Arrival=random.expovariate, AArgs=1 / 10,
#                                         Service=random.expovariate, SArgs=1 / 12, numberJobs=4, doPrint=True,
#                                         infiniteJobs=False).RunSim()
