import simulation, algo, units, buffer, logging, random, reporter
import numpy as np
import networkx as nx

class GridConfig(simulation.SimulationConfig):
    def __init__(self,
                 rows,
                 cols,
                 injection_prob=.5,
                 cycle_number=50,
                 log_level=logging.INFO):
        self.rows = rows
        self.cols = cols
        self.injection_prob = injection_prob
        net = nx.DiGraph()

        self.vert_src = range(cols)
        self.vert_dst = [x + (rows-1)*cols for x in self.vert_src]
        self.horz_src = [x*cols for x in xrange(rows)]
        self.horz_dst = [(x+1)*(cols)-1 for x in xrange(rows)]

        for row in xrange(rows-1):
            for col in xrange(cols):
                net.add_edge(self.get_node(row, col), self.get_node(row+1, col))
                net.add_edge(self.get_node(row+1, col), self.get_node(row, col))

        for row in xrange(rows):
            for col in xrange(cols-1):
                net.add_edge(self.get_node(row, col), self.get_node(row, col+1))
                net.add_edge(self.get_node(row, col+1), self.get_node(row, col))

        self.log_level = log_level
        simulation.SimulationConfig.__init__(self, net, [self], cycle_number=cycle_number, log_level=log_level)

        self.paths = nx.all_pairs_shortest_path(net)

    def get_node(self, row, col):
        return row * self.cols + col

    def invoke_aux(self, src_list, dst_list, packets, curr_cycle):
        for src in src_list:
            if random.random() < self.injection_prob:
                dst = random.choice(dst_list)
                src_route_table = self.paths[src]
                route = src_route_table[dst]
                p = units.Packet('grid', route, curr_cycle)
                packets.append(p)

    def invoke(self, curr_cycle):
        packets = []
        self.invoke_aux(self.vert_src, self.vert_dst, packets, curr_cycle)
        self.invoke_aux(self.horz_src, self.horz_dst, packets, curr_cycle)
        return packets

test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
test3 = simulation.Test('dagdoe', algo.TwoStepsDownHill(), buffer.LongestInSystem, use_pseudo_buffers=True)
tests = [test1, test2, test3]

config = GridConfig(10, 10, .5, 1000,log_level=logging.INFO)
s = simulation.Sim(config, tests)
s.run()

# INFO:results_greedy:Total sent: 10042
# INFO:results_greedy:Total recv: 6059
# INFO:results_greedy:Max packet delay: 671
# INFO:results_greedy:Average packet delay: 131.088958574
# INFO:results_greedy:Max buffer size: 712
# INFO:results_odd_even:Total sent: 10042
# INFO:results_odd_even:Total recv: 3889
# INFO:results_odd_even:Max packet delay: 846
# INFO:results_odd_even:Average packet delay: 234.354332733
# INFO:results_odd_even:Max buffer size: 239
# INFO:results_down_hill:Total sent: 10042
# INFO:results_down_hill:Total recv: 3916
# INFO:results_down_hill:Max packet delay: 755
# INFO:results_down_hill:Average packet delay: 232.408069459
# INFO:results_down_hill:Max buffer size: 239


# test3 = simulation.Test('down_hill', algo.GeneralizedDownHill(use_odd_even=False), buffer.LongestInSystem, reporter.TestResultsAnimation())
# tests = [test3]
# config = GridConfig(3, 3, .1, 1000,log_level=logging.INFO)
# s = simulation.Sim(config, tests)
# s.run()

# INFO:results_greedy:Total sent: 10027
# INFO:results_greedy:Total recv: 10027
# INFO:results_greedy:Max packet delay: 2146
# INFO:results_greedy:Average packet delay: 500.252617932
# INFO:results_greedy:Max buffer size: 748
# INFO:results_odd_even:Total sent: 10027
# INFO:results_odd_even:Total recv: 10027
# INFO:results_odd_even:Max packet delay: 2603
# INFO:results_odd_even:Average packet delay: 899.059140321
# INFO:results_odd_even:Max buffer size: 241
# INFO:results_dagdoe:Total sent: 10027
# INFO:results_dagdoe:Total recv: 10027
# INFO:results_dagdoe:Max packet delay: 2835
# INFO:results_dagdoe:Average packet delay: 922.264086965
# INFO:results_dagdoe:Max buffer size: 214