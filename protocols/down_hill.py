import forwarding_protocol
import forwarding_buffer
import numpy as np
import collections

# DownHill for line graph with C=1
class SimpleDownHill(forwarding_protocol.ForwardingProtocol):
    def __init__(self, use_odd_even=True, buffer_type=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)
        self.use_odd_even = use_odd_even

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        for src, dest in self.network.edges_iter():
            edge_attr = self.test.get_edge_attr(dest, src)
            buf_size = len(edge_attr['buf'])
            assert edge_attr['cap'] == 1, 'SimpleDownHill protocol works for line graphs with C=1'

            if buf_size == 0:
                continue

            dest_buf_size = self.network.node[dest].curr_total_packets
            is_odd = dest_buf_size & 1

            if buf_size > dest_buf_size or self.use_odd_even and buf_size == dest_buf_size and is_odd:
                self.test.forward(dest, src, 1)

# DownHill for trees with any constant C
class DownHillProtocol(forwarding_protocol.ForwardingProtocol):
    def __init__(self, use_odd_even, buffer_type=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)
        self.use_odd_even = use_odd_even
        self.capacity = None

    def init(self, test):
        forwarding_protocol.ForwardingProtocol.init(self, test)

        for n1, n2 in self.network.edges_iter():
            cap = self.network[n1][n2]['cap']
            if not self.capacity:
                self.capacity = cap
            assert cap == self.capacity

    def run_communication_step(self):
        self.to_send = collections.defaultdict(int)
        for node_name in self.network.nodes_iter():
            self.run_communication_step_per_node(node_name)

    def run_communication_step_per_node(self, node_name):
        node = self.network.node[node_name]
        if not node.parents:
            return

        X = [self.test.get_edge_buf_size(node_name, parent) for parent in node.parents]
        buffer_sizes_sum = sum(X)

        if buffer_sizes_sum == 0:
            return

        f = node.curr_total_packets
        ro = self.capacity

        def VL(L):
            return int(np.ceil(float(L)/ro))

        VL_f = VL(f)
        is_odd = VL_f & 1

        max_buffer = np.max(X)
        if self.use_odd_even:
            if not (VL(max_buffer) > VL_f or VL(max_buffer) == VL_f and is_odd):
                return
        else: # Regular downhill
            if VL(max_buffer) <= VL_f:
                return

        def L_j(load, j):
            return load - j + 1

        q = L_j(buffer_sizes_sum, (VL_f - 1)*ro + 1) if is_odd else L_j(buffer_sizes_sum, VL_f * ro + 1)
        num_to_send = min(q, ro)

        while num_to_send > 0:
            argmax = np.argmax(X)
            assert X[argmax] > 0
            X[argmax] -= 1
            parent = node.parents[argmax]
            self.to_send[node.name, parent] += 1
            num_to_send -= 1

    def run_forwarding_step(self):
        for (dest, src), count in self.to_send.iteritems():
            self.test.forward(dest, src, count)

