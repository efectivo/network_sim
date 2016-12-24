import units
import policy
import algo
import network_factory
import buffer


class Sim(object):
    """
    The main class for configuring and running the simulation.
    """
    def __init__(self, alg_type, net, policy_list, buffer_type, cycles=50, verbose=False):
        self.algo = alg_type(self)
        self.net = net
        self.policy = policy_list
        self.cycle_number = cycles
        self.verbose = verbose
        self.reporter = units.Reporter(self)
        self.nodes = {}
        self.curr_cycle = 0

        for node_name in net.nodes():
            node = units.Node(node_name, self, buffer_type)
            self.nodes[node_name] = node

        for policy in policy_list:
            node = self.nodes[policy.src]
            node.add_policy(policy)

    # The cycle has two phases:
    # 1. Each router invokes packets according to its policies
    # 2. Call the algo for packet routing
    def run_cycle(self):
        for node in self.nodes.values():
            node.invoke_packets()

        if self.verbose:
            self.print_state()

        self.algo.run()

        for node in self.nodes.values():
            node.cycle_end()
        self.reporter.cycle_end()

    # The main loop
    def run(self):
        while self.curr_cycle < self.cycle_number:
            self.run_cycle()
            self.curr_cycle += 1

        self.reporter.print_result()
        self.print_state()

    def print_state(self):
        print 'state in cycle: ', self.curr_cycle
        for node in self.nodes.itervalues():
            node.print_state()


if __name__ == '__main__':
    # net = network_factory.create_random_weighted_dag(10)
    net = network_factory.create_path_graph(10)
    # network_factory.draw(net)

    policy = [policy.SendEachCycleRR(0, net, 9), policy.SendEachCycleRR(4, net, 6)]
    cycles = 100
    verbose = False

    s = Sim(algo.PassIfEmpty, net, policy, buffer.LongestInSystem, cycles, verbose)
    s.run()
