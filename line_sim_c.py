from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill
import networkx as nx
import logging, random
import matplotlib.pyplot as plt

writer = results_to_file.ResultHandler('lineC')#, output_dir=r'C:\Users\yairr\Documents\results')

def create_directed_line(N, C):
    net = nx.DiGraph()
    for i in xrange(N):
        net.add_edge(i, i+1, cap=C)
    return net


class rsrd(patterns.PatternIfc):
    def __init__(self, net, node_num, count):
        patterns.PatternIfc.__init__(self, net)
        self.node_num = node_num
        self.count = count

    def invoke_one(self, curr_cycle):
        # Randomize source and destination nodes.
        src = random.randrange(self.node_num)
        dst = self.node_num-1

        # If the least is empty, no packets will be injected on this cycle
        if src == dst:
            return []

        src, dst = min(src, dst), max(src, dst)
        route = range(src, dst + 1)
        # Return a list of packets. In this case only one.
        # The packet is defined by its route (which contains the src and dst nodes)
        return [packet.Packet('RSRD', route, curr_cycle)]

    def invoke(self, curr_cycle):
        return sum([self.invoke_one(curr_cycle) for _ in range(self.count)],[])


N = 100
for C in range(1, 10):
    print C
    cycle_number = 5000
    net = create_directed_line(N, C)
    pattern = rsrd(net, N, C)
    setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=logging.INFO)

    test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
    #test2 = tested_unit.Test('downhill', down_hill.DownHillProtocol(use_odd_even=False))
    test2 = tested_unit.Test('oddeven', down_hill.DownHillProtocol(use_odd_even=True))
    #tests = [test1, test2, test3]
    tests = [test1, test2]

    env = environment.Environment(setup, tests)
    env.run()

    for n, test in enumerate(tests):
        writer.write(str(C), 'RSSD_1_0', cycle_number, test)
