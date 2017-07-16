import sys
sys.path.append('..')
from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill, next_step_down_hill
import networkx as nx
import logging
import random
import matplotlib.pyplot as plt


def create_circle(circle_len):
    net = nx.DiGraph()
    for i in xrange(circle_len-1):
        net.add_edge(i, i + 1)
    net.add_edge(i, 0)
    return net

class CircleRandomSrc(patterns.PatternIfc):
    def __init__(self, net, circle_len):
        patterns.PatternIfc.__init__(self, net)
        self.name = 'random_source'
        self.circle_len = circle_len
        self.dest = self.circle_len - 1
        self.routes = nx.all_pairs_shortest_path(net)

    def invoke(self, curr_cycle):
        src = random.randint(0, self.circle_len - 2)
        route = self.routes[src][self.dest]
        return [packet.Packet(self.name, route, curr_cycle)]

cycle_number = 10000
circle_len = 10
net = create_circle(circle_len)
pattern = CircleRandomSrc(net, circle_len)
setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=logging.INFO)

test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
test2 = tested_unit.Test('odd_even', down_hill.DownHillProtocol(True))
tests = [test1, test2]

env = environment.Environment(setup, tests)
env.run()

