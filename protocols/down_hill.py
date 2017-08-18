import forwarding_protocol
import forwarding_buffer
import numpy as np
import collections
import random

class Types:
    Downhill = 0
    WeakDownhill = 1
    OddEvenDownhill = 2
    DGHybrid = 3
    WGHybrid = 4
    WDHybrid = 5

def type_to_string(t):
    if t == Types.Downhill: return 'Downhill'
    if t == Types.WeakDownhill: return 'WeakDownhill'
    if t == Types.OddEvenDownhill: return 'OddEvenDownhill'
    if t == Types.DGHybrid: return 'DGHybrid'
    if t == Types.WGHybrid: return 'WGHybrid'
    if t == Types.WDHybrid: return 'WDHybrid'
    raise

# DownHill for line graph
class SimpleDownHill(forwarding_protocol.ForwardingProtocol):
    def __init__(self, dh_type, p=1, scheduling_policy=forwarding_buffer.LongestInSystem):
        forwarding_protocol.ForwardingProtocol.__init__(self)
        self.dh_type = dh_type
        self.p = p # Relevant for hybrid types
        self.set_scheduling_policy(scheduling_policy)
        self.capacity = None

        if False: pass
        elif self.dh_type == Types.Downhill: self.should_forward = self.should_forward_downhill
        elif self.dh_type == Types.WeakDownhill: self.should_forward = self.should_forward_weak_downhill
        elif self.dh_type == Types.OddEvenDownhill: self.should_forward = self.should_forward_odd_even
        elif self.dh_type == Types.DGHybrid: self.should_forward = self.should_forward_dgh
        elif self.dh_type == Types.WGHybrid: self.should_forward = self.should_forward_wgh
        elif self.dh_type == Types.WDHybrid: self.should_forward = self.should_forward_wdh
        else: raise

    def init(self, test):
        forwarding_protocol.ForwardingProtocol.init(self, test)

        for n1, n2 in self.network.edges_iter():
            cap = self.network[n1][n2]['cap']
            if not self.capacity:
                self.capacity = cap
            assert cap == self.capacity

        if self.capacity > 1:
            assert self.dh_type == Types.OddEvenDownhill
            self.should_forward = self.should_forward_general_cap_downhill

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        for src, dest in self.network.edges_iter():
            edge_attr = self.test.get_edge_attr(dest, src)
            buf_size = len(edge_attr['buf'])

            if buf_size == 0:
                continue

            dest_buf_size = self.network.node[dest].curr_total_packets

            count = self.should_forward(buf_size, dest_buf_size)
            if count > 0:
                self.test.forward(dest, src, count)

    def should_forward_downhill(self, buf_size, dest_buf_size):
        return 1 if buf_size > dest_buf_size else 0

    def should_forward_weak_downhill(self, buf_size, dest_buf_size):
        return 1 if buf_size >= dest_buf_size else 0

    def should_forward_odd_even(self, buf_size, dest_buf_size):
        is_odd = dest_buf_size & 1
        return 1 if buf_size > dest_buf_size or buf_size == dest_buf_size and is_odd else 0

    def should_forward_dgh(self, buf_size, dest_buf_size):
        return 1 if buf_size > dest_buf_size or random.random() < self.p else 0

    def should_forward_wgh(self, buf_size, dest_buf_size):
        return 1 if buf_size >= dest_buf_size or random.random() < self.p else 0

    def should_forward_wdh(self, buf_size, dest_buf_size):
        return 1 if buf_size > dest_buf_size or buf_size >= dest_buf_size and random.random() < self.p else 0

    def should_forward_general_cap_downhill(self, src_buf_size, dest_buf_size):
        def VL(L):
            return int(np.ceil(float(L) / self.capacity))

        vl_src = VL(src_buf_size)
        vl_dest = VL(dest_buf_size)
        is_odd = vl_dest & 1

        c = self.capacity
        if is_odd:
            if vl_src >= vl_dest:
                r = min(c, src_buf_size - c * (vl_dest - 1))
                assert r >= 0
                return r
            return 0
        else:
            if vl_src > vl_dest:
                r = min(c, src_buf_size - c * vl_dest)
                assert r >= 0
                return r
            return 0


# # DownHill for trees with any constant C
# class DownHillProtocol(forwarding_protocol.ForwardingProtocol):
#     def __init__(self, buffer_type=forwarding_buffer.LongestInSystem):
#         forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type)
#         self.capacity = None
#
#     def init(self, test):
#         forwarding_protocol.ForwardingProtocol.init(self, test)
#
#         for n1, n2 in self.network.edges_iter():
#             cap = self.network[n1][n2]['cap']
#             if not self.capacity:
#                 self.capacity = cap
#             assert cap == self.capacity
#
#     def run_communication_step(self):
#         self.to_send = collections.defaultdict(int)
#         for node_name in self.network.nodes_iter():
#             self.run_communication_step_per_node(node_name)
#
#     def run_communication_step_per_node(self, node_name):
#         node = self.network.node[node_name]
#         if not node.parents:
#             return
#
#         X = [self.test.get_edge_buf_size(node_name, parent) for parent in node.parents]
#         buffer_sizes_sum = sum(X)
#
#         if buffer_sizes_sum == 0:
#             return
#
#         f = node.curr_total_packets
#         ro = self.capacity
#
#         def VL(L):
#             return int(np.ceil(float(L) / ro))
#
#         VL_f = VL(f)
#         is_odd = VL_f & 1
#
#         max_buffer = np.max(X)
#         if self.use_odd_even:
#             if not (VL(max_buffer) > VL_f or VL(max_buffer) == VL_f and is_odd):
#                 return
#         else:  # Regular downhill
#             if VL(max_buffer) <= VL_f:
#                 return
#
#         def L_j(load, j):
#             return max(load - j + 1, 0)
#
#         if is_odd:
#             q = sum([L_j(tmp, (VL_f - 1) * ro + 1) for tmp in X])
#         else:
#             q = sum([L_j(tmp, VL_f * ro + 1) for tmp in X])
#
#         num_to_send = min(q, ro)
#
#         while num_to_send > 0:
#             argmax = np.argmax(X)
#             assert X[argmax] > 0
#             X[argmax] -= 1
#             parent = node.parents[argmax]
#             self.to_send[node.name, parent] += 1
#             num_to_send -= 1
#
#     def run_forwarding_step(self):
#         for (dest, src), count in self.to_send.iteritems():
#             self.test.forward(dest, src, count)
#
