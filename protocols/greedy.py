import forwarding_protocol
import forwarding_buffer

class GreedyProtocol(forwarding_protocol.ForwardingProtocol):
    def __init__(self, buffer_type=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        for src, dest in self.network.edges_iter():
            edge_attr = self.test.get_edge_attr(dest, src)
            buf_size = len(edge_attr['buf'])
            cap = edge_attr['cap']

            if buf_size == 0:
                continue

            count = min(buf_size, cap)
            self.test.forward(dest, src, count)

