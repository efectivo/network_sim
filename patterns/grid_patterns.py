import patterns
import random
from units import packet
from networks import grid
import numpy as np
gn = grid.get_node


class RandomNodesOneBentRoute(patterns.PatternIfc):
    def __init__(self, N, rate):
        self.N = N
        self.rate = rate

    def invoke_one(self, curr_cycle):
        def rand_node():
            row = random.randint(0, self.N - 1)
            col = random.randint(0, self.N - 1)
            return [row, col]

        src = rand_node()
        dest = rand_node()
        while dest == src:
            dest = rand_node()

        # Start with the source
        route = []
        i = src
        while i != dest:
            route.append(gn(self.N, i[0], i[1]))
            if i[0] != dest[0]:
                i[0] += 1 if dest[0] > i[0] else -1
            else:
                i[1] += 1 if dest[1] > i[1] else -1
        route.append(gn(self.N, dest[0], dest[1]))
        return packet.Packet(route, curr_cycle)

    def invoke(self, curr_cycle):
        num_packets = np.random.poisson(self.rate)
        return [self.invoke_one(curr_cycle) for _ in range(num_packets)]
