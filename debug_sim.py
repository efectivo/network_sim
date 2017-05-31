from units import environment, packet, tested_unit
from protocols import forwarding_protocol, greedy, next_step_down_hill
import networkx as nx
import logging

class DebugSetup(environment.EnvironmentSetup):
    def __init__(self, input_degree, output_degree, routes):
        net = nx.DiGraph()

        next_node = 1
        for _ in range(input_degree):
            net.add_edge(next_node, 0)
            next_node += 1

        for _ in range(output_degree):
            net.add_edge(0, next_node)
            next_node += 1

        self.log_level = logging.DEBUG
        environment.EnvironmentSetup.__init__(self, net, [self], cycle_number=1, log_level=self.log_level)

        self.routes = routes

    def invoke(self, curr_cycle):
        if curr_cycle == 0:
            return [packet.Packet('test', route, 0) for route in self.routes]
        return []

test1 = tested_unit.Test('2s', next_step_down_hill.TwoStepsDownHill())
tests = [test1]

#start_packets = [[1, 0, 3], [1, 0, 3], [0, 3], [0, 3], [2, 0, 4], [2, 0, 4]]
#start_packets = [[1,0,3], [0,3], [2,0,3]]
#start_packets = [[1,0,3], [0,3], [2,0,3], [1,0,3], [0,3], [2,0,3]]
#start_packets = [[1,0,3], [0,3], [2,0,4], [1,0,3], [0,3], [2,0,4]]
#start_packets = [[1,0,3], [0,3], [2,0,4], [1,0,3], [0,3], [2,0,4], [0,4], [0,4], [0,3], [0,4]]
#start_packets = [[1,0], [1,0,3], [1,0,4], [0,3], [0,3], [2,0,4], [2,0,4], [2,0,4]]
#start_packets = [[1,0], [1,0,3], [1,0,4], [0,3], [0,3], [2,0,4], [2,0,4], [2,0,4], [0,3]]
start_packets = [[1,0,3], [1,0], [1,0,4]]

config = DebugSetup(2, 2, start_packets)

# net = config.net
# pos = nx.circular_layout(net)
# nx.draw_networkx(net, pos)
# import matplotlib.pyplot as plt
# plt.show()

s = environment.Environment(config, tests)
s.run()



