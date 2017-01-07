import units
import reporter


class Sim(object):
    """
    The main class for configuring and running the simulation.
    """
    def __init__(self, alg_type, net, policy_list, buffer_type, cycle_number=50, verbose=False):
        self.algo = alg_type(self)
        self.net = net
        self.policy_list = policy_list
        self.cycle_number = cycle_number
        self.curr_cycle = 0
        self.verbose = verbose

        self.reporter = reporter.Reporter(self, cycle_number)
        self.nodes = {}

        for node_name in net.nodes():
            node = units.Node(node_name, self, buffer_type)
            self.nodes[node_name] = node

    def invoke_packets(self):
        for p in self.policy_list:
            packets = p.invoke(self.curr_cycle)
            self.reporter.packets_invoked(packets)

            for packet in packets:
                node_name = packet.get_next_hop()
                node = self.nodes[node_name]
                node.receive(packet)

    def run(self):
        while self.curr_cycle < self.cycle_number:
            # Invoke new packets
            self.invoke_packets()

            # Route existing packets
            self.algo.run()

            # Update units
            for node in self.nodes.values():
                node.cycle_end()

            if self.verbose:
                self.print_state()

            self.curr_cycle += 1

        self.reporter.finalize()

    def print_state(self):
        print 'state in cycle: ', self.curr_cycle
        for node in self.nodes.itervalues():
            node.print_state()
