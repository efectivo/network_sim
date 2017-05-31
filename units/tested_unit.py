import test_reporter

class Test(object):
    def __init__(self, name, forwarding_protcol, reporter=None):
        self.name = name
        self.forwarding_protcol = forwarding_protcol
        self.nodes = {}
        if reporter is None:
            reporter = test_reporter.TestResultsSummary()
        self.reporter = reporter
        self.env = None
        self.network = None

    # Initialize the buffers associated with the edges
    def init(self, env):
        self.env = env
        self.network = env.network
        self.forwarding_protcol.set_env(self)
        self.reporter.init(self)

        for node_name in self.network.nodes_iter():
            self.nodes[node_name] = self.forwarding_protcol.create_node(node_name)

        for node in self.nodes.itervalues():
            node.update_topology(self.network, self.nodes)

        self.forwarding_protcol.init()

    def run_communication_step(self):
        self.forwarding_protcol.run_communication_step()

    def run_forwarding_step(self):
        self.forwarding_protcol.run_forwarding_step()

    # The injection step is not explicitly depend on the forwarding protocol
    def run_injection_step(self, packets):
        self.reporter.packets_invoked(packets)

        for packet in packets:
            node_name = packet.get_next_hop()
            node = self.nodes[node_name]
            node.receive(packet)

    def run_reporting_step(self):
        for node in self.nodes.itervalues():
            node.cycle_end()
        self.reporter.cycle_end()

    def finalize(self):
        self.reporter.finalize()
