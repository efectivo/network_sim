import units
import reporter
import logging


class Sim(object):
    """
    The main class for configuring and running the simulation.
    """
    def __init__(self, algo, net, policy_list, buffer_type,
                 cycle_number=50, log_level=logging.INFO,
                 calc_history=False, animate=False):
        self.net = net
        self.policy_list = policy_list
        self.cycle_number = cycle_number
        self.curr_cycle = 0
        logging.basicConfig(level=log_level)
        self.logger = logging.getLogger('sim')
        self.verbose = log_level == logging.DEBUG
        self.reporter = reporter.Reporter(self, calc_history)
        self.animate = animate
        self.nodes = {}

        for node_name in net.nodes():
            node = units.Node(node_name, self, buffer_type)
            self.nodes[node_name] = node

        self.algo = algo
        self.algo.init(self)

    def get_node(self, name):
        return self.nodes[name]

    def invoke_packets(self):
        for p in self.policy_list:
            packets = p.invoke(self.curr_cycle)
            if not packets:
                continue
            self.reporter.packets_invoked(packets)

            for packet in packets:
                node_name = packet.get_next_hop()
                node = self.nodes[node_name]
                node.receive(packet)

    def run(self):
        while self.curr_cycle < self.cycle_number:
            self.logger.debug(self.curr_cycle)
            # Invoke new packets
            self.invoke_packets()

            # Route existing packets
            self.algo.run()

            # Update units
            for node in self.nodes.values():
                node.cycle_end()

            if self.animate:
                self.reporter.animate()

            self.curr_cycle += 1

        self.reporter.finalize()

