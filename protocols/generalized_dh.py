import forwarding_protocol, forwarding_buffer, forwarding_buffer_composite, down_hill
import collections, networkx as nx, numpy as np


class GeneralizedOED(forwarding_protocol.ForwardingProtocol):
    def __init__(self, scheduling_policy=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self)
        self.set_scheduling_policy(lambda: forwarding_buffer_composite.BufferComposite(scheduling_policy))
        self.reversed_net = None
        self.to_send = None

    def init(self, test):
        forwarding_protocol.ForwardingProtocol.init(self, test)
        self.reversed_net = nx.reverse(self.network)

    def run_communication_step(self):
        self.to_send = collections.defaultdict(int)
        for node in self.network.nodes_iter():
            self.run_communication_step_per_node(node)

    def run_communication_step_per_node(self, node):
        # Iterate over the edges e_i independently
        for i in self.reversed_net.edge[node]:
            e_i = self.test.get_edge_attr(node, i)

            cap = e_i['cap']
            buf_composite = e_i['buf']
            e_i_size = len(buf_composite)

            # None means no next hop - terminal packets
            pb = [(buf_composite.get_buf_len(None), None)]

            if self.network.edge[node]:
                pb += [(buf_composite.get_buf_len(j), j) for j in self.network.edge[node].iterkeys()]

            # js are the names of node's children.
            # pb_j is the pseudo buffer in e_i w.r.t j.
            pb_j_sizes, js = zip(*pb)
            pb_j_sizes = list(pb_j_sizes)

            while cap > 0 and sum(pb_j_sizes) > 0:
                # Iteratively choose largest pb
                index = np.argmax(pb_j_sizes)
                j = js[index]

                # Terminal packets
                if j is None:
                    self.to_send[i, node, None] += 1
                    pb_j_sizes[index] -= 1
                    cap -= 1
                    continue

                e_j = self.test.get_edge_attr(j, node)
                e_j_size = len(e_j['buf'])
                if (self.should_forward_odd_even(e_i_size, e_j_size)):
                    self.to_send[i, node, j] += 1
                    pb_j_sizes[index] -= 1
                    cap -= 1
                else:
                    # Set to zero since the OED rule doesn't apply
                    pb_j_sizes[index] = 0

    def should_forward_odd_even(self, buf_size, dest_buf_size):
        is_odd = dest_buf_size & 1
        return 1 if buf_size > dest_buf_size or buf_size == dest_buf_size and is_odd else 0

    def run_forwarding_step(self):
        for (node, next_node, two_steps), count in self.to_send.iteritems():
            self.test.forward(next_node, node, count, two_steps_node=two_steps)
