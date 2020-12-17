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
        choices =[]
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
