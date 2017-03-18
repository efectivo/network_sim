import simulation, policy, algo, units, buffer, logging, random, reporter
import numpy as np
import networkx as nx

class LineHopsConfig(simulation.SimulationConfig):
    def __init__(self,
                 N,
                 average_packets_per_cycle,
                 shortcut_prob,
                 cycle_number=50,
                 log_level=logging.INFO):
        self.N = N
        self.average_packets_per_cycle = average_packets_per_cycle
        self.shortcut_prob = shortcut_prob
        net = nx.DiGraph()

        for i in xrange(N):
            for j in xrange(i+1, N):
                net.add_edge(j, i)

        self.log_level = log_level
        simulation.SimulationConfig.__init__(self, net, [self], cycle_number=cycle_number, log_level=log_level)

    def invoke(self, curr_cycle):
        num_packets = np.random.poisson(self.average_packets_per_cycle)

        packets = []

        for packet in xrange(num_packets):
            src = random.randint(1, self.N-1)
            dst = random.randint(0, src-1)
            if random.random() < self.shortcut_prob and src - dst > 2:
                s1 = random.randint(dst+2, src-1)
                s2 = random.randint(dst+1, s1-1)
                route = range(src, s1-1, -1) + range(s2, dst-1, -1)
            else:
                route = range(src, dst-1, -1)

            p = units.Packet('hops', route, curr_cycle)
            packets.append(p)

        return packets

test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
#test3 = simulation.Test('down_hill', algo.GeneralizedDownHill(use_odd_even=False), buffer.LongestInSystem, reporter.TestResultsAnimation())
#tests = [test3]
test3 = simulation.Test('down_hill', algo.GeneralizedDownHill(use_odd_even=False), buffer.LongestInSystem)
tests = [test1, test2, test3]

#s = simulation.Sim(LineHopsConfig(100, 1, .5, 1000,log_level=logging.INFO), tests)
#s.run()
# INFO:results_greedy:Total sent: 1012
# INFO:results_greedy:Total recv: 987
# INFO:results_greedy:Max packet delay: 9
# INFO:results_greedy:Average packet delay: 0.54609929078
# INFO:results_greedy:Max buffer size: 4
# INFO:results_odd_even:Total sent: 1012
# INFO:results_odd_even:Total recv: 987
# INFO:results_odd_even:Max packet delay: 7
# INFO:results_odd_even:Average packet delay: 0.545086119554
# INFO:results_odd_even:Max buffer size: 3
# INFO:results_down_hill:Total sent: 1012
# INFO:results_down_hill:Total recv: 975
# INFO:results_down_hill:Max packet delay: 57
# INFO:results_down_hill:Average packet delay: 5.91384615385
# INFO:results_down_hill:Max buffer size: 3

s = simulation.Sim(LineHopsConfig(100, 3, .5, 1000,log_level=logging.INFO), tests)
s.run()

# INFO:results_greedy:Total sent: 3017
# INFO:results_greedy:Total recv: 2915
# INFO:results_greedy:Max packet delay: 55
# INFO:results_greedy:Average packet delay: 8.3910806175
# INFO:results_greedy:Max buffer size: 8
# INFO:results_odd_even:Total sent: 3017
# INFO:results_odd_even:Total recv: 2791
# INFO:results_odd_even:Max packet delay: 550
# INFO:results_odd_even:Average packet delay: 39.7968470082
# INFO:results_odd_even:Max buffer size: 13
# INFO:results_down_hill:Total sent: 3017
# INFO:results_down_hill:Total recv: 2249
# INFO:results_down_hill:Max packet delay: 894
# INFO:results_down_hill:Average packet delay: 63.3232547799
# INFO:results_down_hill:Max buffer size: 8