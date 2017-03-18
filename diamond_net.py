import simulation, network_factory, policy, algo, units, buffer, logging, random, reporter
import networkx as nx

class DiamondConfig(simulation.SimulationConfig):
    def __init__(self, L, add_cross_edges_prob, cycle_number=50, log_level=logging.INFO):
        self.L = L
        self.add_cross_edges = add_cross_edges_prob > 0
        self.add_cross_edges_prob = add_cross_edges_prob
        net = nx.DiGraph()

        for i in xrange(L):
            i = i * 3
            net.add_edge(i, i + 1)
            net.add_edge(i, i + 2)
            net.add_edge(i + 1, i + 3)
            net.add_edge(i + 2, i + 3)
            if self.add_cross_edges:
                net.add_edge(i + 1, i + 2)
                net.add_edge(i + 2, i + 1)


        self.log_level = log_level
        simulation.SimulationConfig.__init__(self, net, [self], cycle_number=cycle_number, log_level=log_level)

    def invoke(self, curr_cycle):
        route1 = []
        route2 = []
        dst = 3*self.L
        for i in xrange(self.L):
            i = i * 3
            route1.append(i)
            route2.append(i)
            a1, a2 = (1, 2) if random.random() < .5 else (2, 1)
            route1.append(i+a1)
            route2.append(i+a2)

            if self.add_cross_edges_prob and random.random() < self.add_cross_edges_prob:
                route1.append(i + a2)
                route2.append(i + a1)

        route1.append(dst)
        route2.append(dst)

        start1 = random.randint(0, len(route1)-2)
        start2 = random.randint(0, len(route2)-2)

        p1 = units.Packet('diamond', route1[start1:], curr_cycle)
        p2 = units.Packet('diamond', route2[start2:], curr_cycle)
        return [p1, p2]

# net = DiamondConfig(3, 1).net
# pos = nx.circular_layout(net)
# nx.draw_networkx(net, pos)
# import matplotlib.pyplot as plt
# plt.show()

test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
test3 = simulation.Test('down_hill', algo.GeneralizedDownHill(use_odd_even=False), buffer.LongestInSystem)
tests = [test1, test2, test3]
config = DiamondConfig(20, .3, 1000)
s = simulation.Sim(config, tests)
s.run()

# INFO:results_greedy:Total sent: 2000
# INFO:results_greedy:Total recv: 1915
# INFO:results_greedy:Max packet delay: 43
# INFO:results_greedy:Average packet delay: 16.5577023499
# INFO:results_greedy:Max buffer size: 12
# INFO:results_odd_even:Total sent: 2000
# INFO:results_odd_even:Total recv: 1675
# INFO:results_odd_even:Max packet delay: 172
# INFO:results_odd_even:Average packet delay: 98.4746268657
# INFO:results_odd_even:Max buffer size: 9
# INFO:results_down_hill:Total sent: 2000
# INFO:results_down_hill:Total recv: 1357
# INFO:results_down_hill:Max packet delay: 376
# INFO:results_down_hill:Average packet delay: 189.107590273
# INFO:results_down_hill:Max buffer size: 11


#config = DiamondConfig(200, .3, 1000)
# INFO:results_greedy:Total sent: 2000
# INFO:results_greedy:Total recv: 1244
# INFO:results_greedy:Max packet delay: 316
# INFO:results_greedy:Average packet delay: 70.9356913183
# INFO:results_greedy:Max buffer size: 12
# INFO:results_odd_even:Total sent: 2000
# INFO:results_odd_even:Total recv: 872
# INFO:results_odd_even:Max packet delay: 446
# INFO:results_odd_even:Average packet delay: 113.274082569
# INFO:results_odd_even:Max buffer size: 6
# INFO:results_down_hill:Total sent: 2000
# INFO:results_down_hill:Total recv: 308
# INFO:results_down_hill:Max packet delay: 716
# INFO:results_down_hill:Average packet delay: 403.418831169
# INFO:results_down_hill:Max buffer size: 5