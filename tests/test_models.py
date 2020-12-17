import io
import random
from contextlib import redirect_stdout
from unittest import TestCase

from parallelqueue import base_models


class TestModels(TestCase):
    # Tries all base models
    def test_runall(self):
        base = 0
        sims = [base_models.ParallelQueueSystem(maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                                Replicas=True, Arrival=random.expovariate, AArgs=0.5,
                                                Service=random.expovariate, SArgs=1),
                base_models.JSQd(maxTime=100.0, parallelism=1000, seed=1234,
                                 d=2, Arrival=random.expovariate, AArgs=0.5,
                                 Service=random.expovariate, SArgs=1),
                base_models.RedundancyQueueSystem(maxTime=100.0, parallelism=1000, seed=1234, d=2,
                                                  Arrival=random.expovariate, AArgs=0.5,
                                                  Service=random.expovariate, SArgs=1)]
        for i in sims:
            try:
                i.RunSim()
            except RuntimeError:
                base += 1
        assert base == 0

    def test_simpy(self):
        sim = base_models.JSQd(numberJobs=5, infiniteJobs=False, parallelism=2, seed=12345,
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
        assert original[-1] == test[-2]  # due to change in out

    def test_seed(self):
        # 1 seed should give 1 result across 2 initializations
        base = 0
        sim1 = base_models.JSQd(maxTime=100.0, parallelism=100, seed=1234, d=2,
                                Arrival=random.expovariate, AArgs=0.5,
                                Service=random.expovariate, SArgs=1)
        sim1.RunSim()
        df1 = sim1.DataFrame
        sim2 = base_models.JSQd(maxTime=100.0, parallelism=100, seed=1234, d=2,
                                Arrival=random.expovariate, AArgs=0.5,
                                Service=random.expovariate, SArgs=1)
        sim2.RunSim()
        df2 = sim2.DataFrame
        for i in range(df1.shape[0]):
            for j in range(df1.shape[1]):
                if df1.iloc[i, j] != df2.iloc[i, j]:
                    base += 1
        assert base == 0


#   For test_simpy
"""
Bank with multiple queues example

Covers:

- Resources: Resource
- Iterating processes

Scenario:
  A multi-counter bank with a random service time and customers arrival process. Based on the
  program bank10.py from TheBank tutorial of SimPy 2. (KGM)

By Aaron Janeiro Stone -- Modified from my Medium Article:
https://medium.com/swlh/simulating-a-parallel-queueing-system-with-simpy-6b7fcb6b1ca1
"""
import io
import random
from contextlib import redirect_stdout

from simpy import *


def RunSim():
    global Customer, NoInSystem
    maxNumber = 5  # Max number of customers
    seed = 12345  # Seed for simulation
    arrivalMean = 1

    def Customer(env, name, counters):
        arrive = env.now
        Qlength = [NoInSystem(counters[i]) for i in range(len(counters))]
        print("%7.4f %s: Here I am. %s" % (env.now, name, Qlength))
        choices = []
        for i in range(len(Qlength)):
            if Qlength[i] in [0, min(Qlength)]:
                choices.append(i)  # the chosen queue number; can be > 1

        if len(choices) > 1:
            choice = random.sample(choices, 1)[0]
        else:
            choice = choices[0]

        with counters[choice].request() as req:
            # Wait for the counter
            yield req
            wait = env.now - arrive
            # We got to the counter
            print('%7.4f %s: Waited %6.3f' % (env.now, name, wait))
            tib = random.expovariate(1 / 10)
            yield env.timeout(tib)
            print('%7.4f %s: Finished' % (env.now, name))

    def NoInSystem(R):
        """Total number of customers in the resource R"""
        return max([0, len(R.put_queue) + len(R.users)])

    def Source(env, number, interval, counters):
        for i in range(number):
            c = Customer(env, 'Customer%02d' % i, counters)
            env.process(c)
            t = random.expovariate(1.0)
            yield env.timeout(t)

    # Setup and start the simulation
    print('Bank with multiple queues')
    random.seed(seed)
    env = Environment()
    counters = [Resource(env), Resource(env)]
    env.process(Source(env, maxNumber, arrivalMean, counters))
    env.run()


def SimTest():
    f = io.StringIO()
    with redirect_stdout(f):
        RunSim()
    ls = f.getvalue().split(" ")
    test = []
    for i in ls:
        try:
            test.append(float(i))
        except:
            pass
    return test
