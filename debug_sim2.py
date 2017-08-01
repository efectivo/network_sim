from units import environment, packet, tested_unit, test_reporter
from protocols import forwarding_protocol, greedy, next_step_down_hill
import networkx as nx
import logging
from protocols import down_hill

class DebugSetup(environment.EnvironmentSetup):
    def __init__(self, N, C, routes):
        self.routes = routes
        net = nx.DiGraph()
        for i in xrange(N):
            net.add_edge(i, i + 1, cap=C)

        self.log_level = logging.DEBUG
        environment.EnvironmentSetup.__init__(self, net, [self], cycle_number=1, log_level=self.log_level)

    def invoke(self, curr_cycle):
        if curr_cycle == 0:
            return [packet.Packet('test', route, 0) for route in self.routes]
        return []



test1 = tested_unit.Test('greedy', greedy.GreedyProtocol(), reporter=test_reporter.TestResultsLog(r'c:\Temp\bla3'))
test2 = tested_unit.Test('sim_odd_even', down_hill.SimpleDownHill(use_odd_even=True), reporter=test_reporter.TestResultsLog(r'c:\Temp\bla'))
test3 = tested_unit.Test('odd_even', down_hill.DownHillProtocol(use_odd_even=True), reporter=test_reporter.TestResultsLog(r'c:\Temp\bla2'))
tests = [test1, test2, test3]

start_packets = [[0,1,2,3], [0,1,2,3], [0,1,2,3]]
config = DebugSetup(5, 1, start_packets)

s = environment.Environment(config, tests)
s.run()



