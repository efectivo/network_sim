import simulation, network_factory, policy, algo, units, buffer, logging, random, reporter
import networkx as nx

class DiamondConfig(simulation.SimulationConfig):
    def __init__(self, L, cycle_number=50, log_level=logging.INFO):
        self.L = L
        net = nx.DiGraph()

        for i in xrange(L):
            i = i * 3
            net.add_edge(i, i + 1)
            net.add_edge(i, i + 2)
            net.add_edge(i + 1, i + 3)
            net.add_edge(i + 2, i + 3)

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
        route1.append(dst)
        route2.append(dst)

        start1 = random.randint(0, len(route1)-2)
        start2 = random.randint(0, len(route2)-2)

        p1 = units.Packet('diamond', route1[start1:], curr_cycle)
        p2 = units.Packet('diamond', route2[start2:], curr_cycle)
        return [p1, p2]

# net = DiamondConfig(3).net
# pos = nx.circular_layout(net)
# nx.draw_networkx(net, pos)

# Configuration for trees
test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
test3 = simulation.Test('down_hill', algo.GeneralizedDownHill(use_odd_even=False), buffer.LongestInSystem)
tests = [test1, test2, test3]
s = simulation.Sim(DiamondConfig(20, 1000), tests)
s.run()
