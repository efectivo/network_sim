import forwarding_protocol
import forwarding_buffer

class GreedyProtocol(forwarding_protocol.ForwardingProtocol):
    def __init__(self, buffer_type=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)
        self.name = 'greedy'

    def run_communication_step(self):
        self.to_send = {}
        for node in self.nodes.itervalues():
            self.run_communication_step_per_node(node)

    def run_communication_step_per_node(self, node):
        for parent in node.parents:
            buf = parent.buffers[node.name]
            if len(buf) == 0:
                continue
            self.to_send[parent, node.name] = min(len(buf), node.edge_capacity_per_parent[parent.name])

    def run_forwarding_step(self):
        for (node, next_node_name), buf_len in self.to_send.iteritems():
            node.send(next_node_name, buf_len)

