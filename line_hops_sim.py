import sys
sys.path.append(r'..')
from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill, forwarding_buffer, next_step_down_hill
import networkx as nx
import logging
import matplotlib.pyplot as plt
import numpy as np
import random

def create_net(N):
    net = nx.DiGraph()
    for i in xrange(N):
        for j in xrange(i + 1, N):
            net.add_edge(j, i)
    return net

class LineHopsPattern(patterns.PatternIfc):
    def __init__(self,
                 net,
                 N,
                 average_packets_per_cycle,
                 shortcut_prob):
        patterns.PatternIfc.__init__(self, net)
        self.N = N
        self.average_packets_per_cycle = average_packets_per_cycle
        self.shortcut_prob = shortcut_prob

    def invoke(self, curr_cycle):
        num_packets = np.random.poisson(self.average_packets_per_cycle)

        packets = []

        for _ in range(num_packets):
            src = random.randint(1, self.N-1)
            dst = random.randint(0, src-1)
            if random.random() < self.shortcut_prob and src - dst > 2:
                s1 = random.randint(dst+2, src-1)
                s2 = random.randint(dst+1, s1-1)
                route = range(src, s1-1, -1) + range(s2, dst-1, -1)
            else:
                route = range(src, dst-1, -1)

            p = packet.Packet('hops', route, curr_cycle)
            packets.append(p)

        return packets

writer = results_to_file.ResultHandler('hops')

#sizes = [10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
sizes = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50]
for N in sizes:
    #cycle_number = max(1000, N**2)
    cycle_number = 10000
    net = create_net(N)

    #for shortcut_prob in [0, .25, .5, .75, 1]:
    for shortcut_prob in [1,]:
        #for average_packets_per_cycle in [1, 2, 3, 4]:
        for average_packets_per_cycle in [1.5, 2]:
            print N, shortcut_prob, average_packets_per_cycle
            pattern = LineHopsPattern(net, N, average_packets_per_cycle, shortcut_prob)
            log_level = logging.ERROR
            setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=log_level)
            test_num = 1

            for _ in range(test_num):
                test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
                test2 = tested_unit.Test('2s_odd_even', next_step_down_hill.TwoStepsDownHill())
                tests = [test1, test2]

                env = environment.Environment(setup, tests)
                env.run()

                for n, test in enumerate(tests):
                    writer.write(str(N), 'Hops_{}_{}'.format(average_packets_per_cycle, shortcut_prob), cycle_number, test)
