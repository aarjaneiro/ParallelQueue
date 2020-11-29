Examples
********

Join the Shortest Queue
=======================

This example is a translation of this `example <https://pythonhosted.org/SimPy/Tutorials/TheBank.html#several-counters-with-individual-queues>`_ from SimPy Classic. In this scenario, we are implementing what is known as the Join the Shortest Queue (JSQ) algorithm, wherein a job will choose the queue with the smallest wait time. In our DES universe, the jobs will be “Customers” and the servers will be “Counters” at a bank. There are two counters currently servicing patrons and the patrons are smart enough to not to join the bigger of the two lines.

To start, let us run our system until either 30 customers are generated and complete their time in the environment or if some period of time (400 arbitrary units of time) have passed. Let us also choose an average time for each customer to spend in the bank and the mean of our arrival process. For simplicity, we will assume both the service and arrival processes to be exponential.

.. code-block:: python

    from parallelqueue.base_models import ParallelQueueSystem
    sim = ParallelQueueSystem(numberJobs=30, maxTime=400, meanServer=20, arrivalMean=10, seed=12345, doPrint=True,
    d=1,            # We choose exactly one queue per job
    parallelism=2,  # There are a total of two queues to choose from per job
    df = True       # returns a dataframe
    ).RunSim()      # Runs the simulation

Now, with our dataframe, we can visualize the queue loads over time by running:

    .. code-block:: python

        from matplotlib import pyplot as plt
        sim.plot()
        plt.show()