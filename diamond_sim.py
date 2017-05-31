import sys
sys.path.append('..')
from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill, next_step_down_hill
import networkx as nx
import logging
import random
import matplotlib.pyplot as plt

writer = results_to_file.ResultHandler('diamond')

def create_diamond(L, add_cross_edges):
    net = nx.DiGraph()
    for i in xrange(L):
        i = i * 3
        net.add_edge(i, i + 1)
        net.add_edge(i, i + 2)
        net.add_edge(i + 1, i + 3)
        net.add_edge(i + 2, i + 3)
        if add_cross_edges:
            net.add_edge(i + 1, i + 2)
            net.add_edge(i + 2, i + 1)
    return net

class DiamondRandomSrc(patterns.PatternIfc):
    def __init__(self, net, L, packet_num_in_cycle):
        patterns.PatternIfc.__init__(self, net)
        self.name = 'diamond'
        self.L = L
        self.add_cross_edges_prob = 0
        self.packet_num_in_cycle = packet_num_in_cycle

    # def invoke(self, curr_cycle):
    #     route1 = []
    #     route2 = []
    #     dst = 3*self.L
    #     for i in xrange(self.L):
    #         i = i * 3
    #         route1.append(i)
    #         route2.append(i)
    #         a1, a2 = (1, 2) if random.random() < .5 else (2, 1)
    #         route1.append(i+a1)
    #         route2.append(i+a2)
    #
    #         if self.add_cross_edges_prob and random.random() < self.add_cross_edges_prob:
    #             route1.append(i + a2)
    #             route2.append(i + a1)
    #
    #     route1.append(dst)
    #     route2.append(dst)
    #
    #     start1 = random.randint(0, len(route1)-2)
    #     start2 = random.randint(0, len(route2)-2)
    #
    #     p1 = packet.Packet('diamond', route1[start1:], curr_cycle)
    #     p2 = packet.Packet('diamond', route2[start2:], curr_cycle)
    #     return [p1, p2]

    def invoke(self, curr_cycle):
        def invoke_one():
            route1 = []
            dst = 3*self.L
            for i in xrange(self.L):
                i = i * 3
                route1.append(i)
                a1, a2 = (1, 2) if random.random() < .5 else (2, 1)
                route1.append(i+a1)

                if self.add_cross_edges_prob and random.random() < self.add_cross_edges_prob:
                    route1.append(i + a2)

            route1.append(dst)

            start1 = random.randint(0, len(route1)-2)

            p1 = packet.Packet('diamond', route1[start1:], curr_cycle)
            return p1
        return [invoke_one() for _ in range(self.packet_num_in_cycle)]

for L in xrange(1, 100):
#for L in [20,]:
    print L

    #cycle_number = 3000#3*(L**2)
    #cycle_number = max(3000, L**2)
    cycle_number = 100000
    test_num = 1

    for packet_num_in_cycle in [1, 2]:
        net = create_diamond(L, False)
        pattern = DiamondRandomSrc(net, L, packet_num_in_cycle)
        setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=logging.INFO)

        for _ in range(test_num):
            test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
            test2 = tested_unit.Test('2s_odd_even', next_step_down_hill.TwoStepsDownHill())
            tests = [test1, test2]
            #tests = [test2]

            env = environment.Environment(setup, tests)
            env.run()

            for n, test in enumerate(tests):
                writer.write(str(L), 'DiamondRand_{}'.format(packet_num_in_cycle), cycle_number, test)

# import pickle
# with open(r'E:\TOAR2\Network\Latex\results\line.pickle', 'wb') as f:
#     pickle.dump(res, f)
# markers = 'x.ov'
# for n in xrange(test_types_num):
#     plt.scatter(*zip(*res[n]), marker=markers[n])
# plt.show()
