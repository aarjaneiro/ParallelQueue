******************
SimPy Introduction
******************

SimPy is a Discrete Event Simulation (DES) package for Python. DES refers to a simulation system which will periodically introduce a specified event as it runs, discrete insofar as each event can be thought of as “happened” or “not happened (yet, or ever)”.

In SimPy, the DES system is contained within its Environment class. The user specifies a system which will run for the Environment upon executing :code:`Environment.run()`.

Within the Environment , the user can define Process and Resource objects which will dynamically interact as the DES is run. In particular, Process objects are the generators of the discrete events we will be working with while a Resource defines an object to be interacted with in this DES “universe”.

In Python, generator objects can be thought of as distinct from functions. Whereas functions have the form of (for some manipulation, :code:`foo(a)`, like :code:`a+2` ):

.. code-block:: python

    def function(a):
        return foo(a)

generators have the form of:

.. code-block:: python

    def generator(a):
        yield foo(a)

where :code:`yield` instead denotes a single output which will not cause the generator itself to stop being considered. To make this clear, it is possible to have:

.. code-block:: python

    def generator(a):
        yield foo(a)
        print('Wait, I forgot this!')
        yield bar(a)

which is useful for an object which will be existing in our universe for a period of time. Return would instead immediately end the function and output :code:`foo(a)`. For a more concrete example, consider:

.. code-block:: python

   def generator(a):
        yield print(a)
        print('Wait, I forgot this!')
        yield print(a + 1)
    gen = generator(1)

which, when evaluating with the :code:`next` command, gives us:

.. code-block:: python

    >>> next(gen)
    1
    >>> next(gen)
    Wait, I forgot this!
    2

In the end, we now have a way to progress an object in some form of time by taking "steps".