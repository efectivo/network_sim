import timeit
import sys
sys.path.append('..')
from units import environment, packet, tested_unit, patterns, test_reporter, results_to_file
from protocols import forwarding_protocol, greedy, down_hill
import networkx as nx
import logging
import matplotlib.pyplot as plt

writer = results_to_file.ResultHandler('line')

def create_directed_line(N):
    net = nx.DiGraph()
    for i in xrange(N):
        net.add_edge(i + 1, i)
    return net

for N in range(10, 510, 10):
    cycle_number = 50000
    test_num = 1
    net = create_directed_line(N)
    pattern = patterns.RandomSrcSameDest(net, range(1, N), 0)
    setup = environment.EnvironmentSetup(net, [pattern], cycle_number=cycle_number, log_level=logging.ERROR)

    print N
    for _ in range(test_num):
        print _
        if N <= 100:
            test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
            test2 = tested_unit.Test('downhill', down_hill.DownHillProtocol(use_odd_even=False))
            test3 = tested_unit.Test('oddeven', down_hill.DownHillProtocol(use_odd_even=True))
            tests = [test1, test2, test3]
        else:
            test1 = tested_unit.Test('greedy', greedy.GreedyProtocol())
            test2 = tested_unit.Test('oddeven', down_hill.DownHillProtocol(use_odd_even=True))
            tests = [test1, test2]

        env = environment.Environment(setup, tests)
        env.run()

        for n, test in enumerate(tests):
            writer.write('{}'.format(N), 'RSSD_1_0', cycle_number, test)
