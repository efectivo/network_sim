import networkx as nx
import numpy as np
import random
import packet

class PatternIfc(object):
    def __init__(self, net):
        self.net = net

    def invoke(self, curr_cycle):
        return []


class RandomSrcSameDest(PatternIfc):
    def __init__(self, net, src_list, dst):
        PatternIfc.__init__(self, net)
        self.name = 'rssd'
        self.dst = dst
        self.src_max_index = len(src_list) - 1
        self.routes = [nx.shortest_path(net, source=src, target=dst) for src in src_list]

    def invoke(self, curr_cycle):
        src_index = random.randint(0, self.src_max_index)
        return [packet.Packet(self.name, self.routes[src_index], curr_cycle)]

class RandomSrcRandomDest(PatternIfc):
    def __init__(self, net, node_list):
        PatternIfc.__init__(self, net)
        self.name = 'rsrd'
        self.src_max_index = len(node_list) - 1

    def invoke(self, curr_cycle):
        def invoke_packet():
            src = random.randint(0, self.src_max_index)
            dst = src
            while dst == src:
                dst = random.randint(0, self.src_max_index)
            if src < dst:
                route = np.arange(src, dst+1)
            else:
                route = np.arange(src, dst-1, -1)
            return packet.Packet(self.name, route, curr_cycle)

        return [invoke_packet(), invoke_packet()]

# class OnOff(PatternIfc):
#     def __init__(self, net, src, dst, p_on, p_off, n_packets=1):
#         Policy.__init__(self, net)
#         self.name = '{}<-{}'.format(dst, src)
#         self.src = src
#         self.dst = dst
#         self.route = nx.shortest_path(self.net, self.src, self.dst)
#         self.p_on = p_on
#         self.p_off = p_off
#         self.invoke = self.invoke_off
#         self.n_packets = n_packets
#
#     # In OFF state, with p_on switch to ON
#     def invoke_off(self, curr_cycle):
#         if random.random() > self.p_on:
#             return []
#         self.invoke = self.invoke_on
#         return self.invoke_packets(curr_cycle)
#
#     def invoke_on(self, curr_cycle):
#         if random.random() < self.p_off:
#             self.invoke = self.invoke_off
#         return self.invoke_packets(curr_cycle)
#
#     def invoke_packets(self, curr_cycle):
#         return [units.Packet(self.name, self.route, curr_cycle) for _ in xrange(self.n_packets)]
#
#




