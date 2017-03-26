import simulation, network_factory, policy, algo, units, buffer, logging, random, reporter
import networkx as nx

class TesterConfig(simulation.SimulationConfig):
    def __init__(self, input_degree, output_degree, start_packets):
        net = nx.DiGraph()

        next_node = 1
        for _ in range(input_degree):
            net.add_edge(next_node, 0)
            next_node += 1

        for _ in range(output_degree):
            net.add_edge(0, next_node)
            next_node += 1

        self.log_level = logging.DEBUG
        simulation.SimulationConfig.__init__(self, net, [self], cycle_number=2, log_level=self.log_level)

        self.start_packets = start_packets

    def invoke(self, curr_cycle):
        if curr_cycle == 0:
            return [units.Packet('test', route, 0) for route in self.start_packets]
        return []

#test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
#test1 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
test1 = simulation.Test('dagdoe', algo.TwoStepsDownHill(), buffer.LongestInSystem, use_pseudo_buffers=True)

tests = [test1]

#start_packets = [[1, 0, 3], [1, 0, 4], [0, 4]]
start_packets = [[1, 0, 3], [1, 0, 3], [0, 3], [0, 3], [2, 0, 4], [2, 0, 4]]

config = TesterConfig(2, 2, start_packets)

# net = config.net
# pos = nx.circular_layout(net)
# nx.draw_networkx(net, pos)
# import matplotlib.pyplot as plt
# plt.show()

s = simulation.Sim(config, tests)
s.run()


