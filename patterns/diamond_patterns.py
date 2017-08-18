import patterns
import random
from units import packet
import numpy as np


class UniformPoissonRate(patterns.PatternIfc):
    def __init__(self, N, k, dashed, rate):
        self.N = N
        self.k = k
        self.rate = rate
        self.dashed = dashed

    def invoke(self, curr_cycle):
        def invoke_one():
            route = []

            s = 0
            for i in xrange(self.N):
                route.append(s)
                a1 = random.randint(1, self.k)
                route.append(s+a1)

                if self.dashed:
                    route.append(s + self.k + 1)
                    s += self.k + 2
                else:
                    s += self.k + 1
            route.append(s)
            start = random.randint(0, len(route)-2)
            p = packet.Packet(route[start:], curr_cycle)
            return p

        num_packets = np.random.poisson(self.rate * self.k)
        return [invoke_one() for _ in range(num_packets)]
