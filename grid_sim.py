import sys
sys.path.append(r'..')
from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill, forwarding_buffer, next_step_down_hill
import networkx as nx
import logging
import matplotlib.pyplot as plt
import numpy as np
import random

class GridPattern(patterns.PatternIfc):
    def __init__(self,
                 rows,
                 cols,
                 injection_prob=.5):
        self.rows = rows
        self.cols = cols
        self.injection_prob = injection_prob
        net = nx.DiGraph()
        patterns.PatternIfc.__init__(self, net)

        self.vert_src = range(cols)
        self.vert_dst = [x + (rows-1)*cols for x in self.vert_src]
        self.horz_src = [x*cols for x in xrange(rows)]
        self.horz_dst = [(x+1)*(cols)-1 for x in xrange(rows)]

        for row in xrange(rows-1):
            for col in xrange(cols):
                net.add_edge(self.get_node(row, col), self.get_node(row+1, col))
                net.add_edge(self.get_node(row+1, col), self.get_node(row, col))

        for row in xrange(rows):
            for col in xrange(cols-1):
                net.add_edge(self.get_node(row, col), self.get_node(row, col+1))
                net.add_edge(self.get_node(row, col+1), self.get_node(row, col))

        self.net = net
        self.paths = nx.all_pairs_shortest_path(net)

    def get_node(self, row, col):
        return row * self.cols + col

    def invoke_aux(self, src_list, dst_list, packets, curr_cycle):
        for src in src_list:
            if random.random() < self.injection_prob:
                dst = random.choice(dst_list)
                src_route_table = self.paths[src]
                route = src_route_table[dst]
                p = packet.Packet('grid', route, curr_cycle)
                packets.append(p)

    def invoke(self, curr_cycle):
        packets = []
        self.invoke_aux(self.vert_src, self.vert_dst, packets, curr_cycle)
        self.invoke_aux(self.horz_src, self.horz_dst, packets, curr_cycle)
        return packets

writer = results_to_file.ResultHandler('grid')

log_level = logging.ERROR
for N in [5, 10, 15, 20, 25, 30]:
    rows, cols = N, N
    #for injection_prob in [.1, .25, .5]:
    for injection_prob in [.1,]:
        print N, injection_prob
        cycle_number = 10000
        pattern = GridPattern(rows, cols, injection_prob)
        net = pattern.net

        setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=log_level)
        test_num = 1

        for _ in range(test_num):
            test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
            test2 = tested_unit.Test('2s_odd_even', next_step_down_hill.TwoStepsDownHill())
            tests = [test1, test2]

            env = environment.Environment(setup, tests)
            env.run()

            for n, test in enumerate(tests):
                writer.write('{}x{}'.format(rows, cols), 'Grid_{}'.format(injection_prob), cycle_number, test)
