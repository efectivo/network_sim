import simulation, policy, algo, units, buffer, logging, random, reporter
import networkx as nx

class LineConfig(simulation.SimulationConfig):
    def __init__(self, N, cycle_number=50, log_level=logging.INFO):
        self.N = N
        net = nx.DiGraph()

        for i in xrange(N):
            net.add_edge(i+1, i)

        self.log_level = log_level
        simulation.SimulationConfig.__init__(self, net, [self], cycle_number=cycle_number, log_level=log_level)

    def invoke(self, curr_cycle):
        dst = 0
        src = random.randint(0, self.N-1)
        route = range(src, dst-1, -1)

        p = units.Packet('line', route, curr_cycle)
        return [p]

test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.GeneralizedDownHill(use_odd_even=True), buffer.LongestInSystem)
test3 = simulation.Test('dagdoe', algo.Dagdoe(), buffer.LongestInSystem, use_pseudo_buffers=True)
tests = [test1, test2, test3]
s = simulation.Sim(LineConfig(100, 1000,log_level=logging.INFO), tests)
s.run()


# INFO:results_greedy:Total sent: 1000
# INFO:results_greedy:Total recv: 940
# INFO:results_greedy:Max packet delay: 49
# INFO:results_greedy:Average packet delay: 6.41489361702
# INFO:results_greedy:Max buffer size: 5
# INFO:results_odd_even:Total sent: 1000
# INFO:results_odd_even:Total recv: 940
# INFO:results_odd_even:Max packet delay: 38
# INFO:results_odd_even:Average packet delay: 6.52978723404
# INFO:results_odd_even:Max buffer size: 3
# INFO:results_down_hill:Total sent: 1000
# INFO:results_down_hill:Total recv: 511
# INFO:results_down_hill:Max packet delay: 530
# INFO:results_down_hill:Average packet delay: 208.217221135
# INFO:results_down_hill:Max buffer size: 7
