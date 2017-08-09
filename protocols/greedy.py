import forwarding_protocol
import forwarding_buffer

class GreedyProtocol(forwarding_protocol.ForwardingProtocol):
    def __init__(self, scheduling_policy=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self)
        self.set_scheduling_policy(scheduling_policy)

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

