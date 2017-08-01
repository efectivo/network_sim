import test_reporter
import collections

class Test(object):
    def __init__(self, name, forwarding_protcol, reporter=None):
        self.name = name
        self.forwarding_protcol = forwarding_protcol

        if reporter is None:
            reporter = test_reporter.TestResultsSummary()
        self.reporter = reporter

    # The next functions are called by the environment
    def init(self, env):
        self.env = env
        # Create a copy since each test has it's own buffer state
        self.network = env.network.copy()
        self.reporter.init(self)

        # Initialize the nodes and the buffers associated with the edges
        for node_name in self.network.nodes_iter():
            self.network.node[node_name] = self.forwarding_protcol.create_node(node_name, self.network)
        for n1, n2 in self.network.edges_iter():
            self.network[n1][n2]['buf'] = self.forwarding_protcol.create_buffer()

        self.forwarding_protcol.init(self)
        self.received_packets = collections.defaultdict(list)

    def run_communication_step(self):
        self.forwarding_protcol.run_communication_step()

    def run_forwarding_step(self):
        self.forwarding_protcol.run_forwarding_step()

    def run_injection_step(self, packets):
        for packet in packets:
            node_name = packet.get_next_hop()
            self._forward(node_name, None, packet)

    def run_reporting_step(self):
        self._digest_received_packets()
        self.reporter.cycle_end()

    def finalize(self):
        self.reporter.finalize()

    # The next functions are called by the forwarding protocol
    def forward(self, dest, src, count, **kvdict):
        buf = self.network[src][dest]['buf']
        assert len(buf) >= count, 'Invalid forward request {}/{}'.format(count, len(buf))
        for i in xrange(count):
            packet = buf.extract(**kvdict)
            self._forward(dest, src, packet)

    def get_edge_attr(self, dest, src):
        return self.network.edge[src][dest]

    def get_edge_buf_size(self, dest, src):
        return len(self.get_edge_attr(dest, src)['buf'])

    # Internal functions
    # Forward a packet from the edge (src, dest) to (dest, next_node)
    # src might be null in case of invoked function
    # next_node is null when reaching the destination
    def _forward(self, dest, src, packet):
        if src == None:
            self.reporter.packet_invoked(packet)
        else:
            self.reporter.packet_forwarded(dest, src, packet)

        packet.packet_received()
        next_node = packet.get_next_hop()

        # Packet has reached destination
        if next_node is None:
            self.network.node[src].update_total_packets(-1)
            self.reporter.packet_received(packet)
            return

        # Received packets are queued, so they won't sent again in this cycle
        self.received_packets[next_node, dest, src].append(packet)

    def _digest_received_packets(self):
        for (next_node, dest, src), packets in self.received_packets.iteritems():
            for packet in packets:
                buf = self.network[dest][next_node]['buf']
                buf.insert(packet)
                self.network.node[dest].update_total_packets(1)
                if src is not None:
                    self.network.node[src].update_total_packets(-1)
        self.received_packets = collections.defaultdict(list)
