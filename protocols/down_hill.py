import forwarding_protocol
import forwarding_buffer
import numpy as np

# Implemented for nodes with multiple parents and a single child
class DownHillProtocol(forwarding_protocol.ForwardingProtocol):
    def __init__(self, use_odd_even, buffer_type=forwarding_buffer.LongestInSystem):
        self.use_odd_even = use_odd_even
        self.name = 'odd-even' if use_odd_even else 'downhill'
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)

    def run_communication_step(self):
        self.to_send = {}
        for node in self.nodes.itervalues():
            self.run_communication_step_per_node(node)

    def run_communication_step_per_node(self, node):
        if not node.parents:
            return

        buffer_sizes = np.array([len(parent.buffers[node.name]) for parent in node.parents])
        max_size, argmax = np.max(buffer_sizes), np.argmax(buffer_sizes)

        curr_buf_size = node.curr_total_packets
        # Forward the packets odd even downhill
        if max_size > curr_buf_size or self.use_odd_even and max_size == curr_buf_size and (max_size % 2) == 1:
            self.to_send[node.parents[argmax], node.name] = min(max_size, node.edge_capacity_per_parent[parent.name])

    def run_forwarding_step(self):
        for (node, next_node_name), buf_len in self.to_send.iteritems():
            node.send(next_node_name, buf_len)

