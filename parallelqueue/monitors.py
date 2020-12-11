"""
This optional module contains methods for visualization.
"""
from statsmodels.distributions import ECDF


class EmpiricalDistribution:
    def __init__(self, Y, t):
        """
        .. math::

            \\frac{1}{n} \\sum_{i=1}^{n}\\mathbb{1}_{X_{i} \\leq t}

        :param Y: The random variable (in this case, queues). Let Size(Y) = X as in the usual definition.
        :type Y: dict(Resource(Environment))
        :param t: The variable for which :math:`\\mathbb{1}_{X_{i} \\leq t}` is calculated across all X.
        :type t: float
        :return: :math:`x \\in [0,1]`
        :rtype: float

        """
        self.y = Y
        self.IList = [1 if (i.queue + i.users) <= t else 0 for i in self.y]

    def Calculate(self):
        return sum(self.IList) / len(self.IList)

    def sm_calculation(self, side='left'):
        """
        Using statsmodels.
        """
        return ECDF([i.queue + i.users for i in self.y], side)

    @property
    def I_List(self):
        """
        Returns the set of I's
        """
        return self.IList







