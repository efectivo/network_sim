import units
import networkx as nx
import random


class Policy(object):
    def __init__(self, net):
        self.net = net

    def invoke(self, curr_cycle):
        assert False

    # Assert that the injection policy is valid
    def update_load(self, p, packets_per_cycle):
        start_node = p[0]
        for i in xrange(1, len(p)):
            end_node = p[i]
            d = self.net.get_edge_data(start_node, end_node)
            assert d is not None
            if 'load' not in d:
                d['load'] = 0
            if 'cap' not in d:
                d['cap'] = 1

            d['load'] += packets_per_cycle
            assert d['load'] <= d['cap']
            start_node = end_node


class SendEachCycleRR(Policy):
    def __init__(self, src, net, dst):
        Policy.__init__(self, net)
        self.name = 'sec_{}->{}'.format(src, dst)
        self.all_paths = list(nx.all_simple_paths(net, source=src, target=dst))
        for p in self.all_paths:
            self.update_load(p, 1./len(self.all_paths))
        self.curr_path = 0

    def invoke(self, curr_cycle):
        p = units.Packet(self.name, self.all_paths[self.curr_path], curr_cycle)
        self.curr_path = (self.curr_path + 1) % len(self.all_paths)
        return [p]


class RandomSrcSameDest(Policy):
    def __init__(self, net, src_list, dst):
        Policy.__init__(self, net)
        self.dst = dst
        self.src_list = src_list
        self.src_max_index = len(src_list) - 1
        self.name = '{}<-'.format(dst)
        self.paths = nx.all_pairs_shortest_path(net)

    def invoke(self, curr_cycle):
        src = self.src_list[random.randint(0, self.src_max_index)]
        path = self.paths[src][self.dst]
        p = units.Packet(self.name+str(src), path, curr_cycle)
        return [p]


class OnOff(Policy):
    def __init__(self, net, src, dst, p_on, p_off, n_packets=1):
        Policy.__init__(self, net)
        self.name = '{}<-{}'.format(dst, src)
        self.src = src
        self.dst = dst
        self.route = nx.shortest_path(self.net, self.src, self.dst)
        self.p_on = p_on
        self.p_off = p_off
        self.invoke = self.invoke_off
        self.n_packets = n_packets

    # In OFF state, with p_on switch to ON
    def invoke_off(self, curr_cycle):
        if random.random() > self.p_on:
            return []
        self.invoke = self.invoke_on
        return self.invoke_packets(curr_cycle)

    def invoke_on(self, curr_cycle):
        if random.random() < self.p_off:
            self.invoke = self.invoke_off
        return self.invoke_packets(curr_cycle)

    def invoke_packets(self, curr_cycle):
        return [units.Packet(self.name, self.route, curr_cycle) for _ in xrange(self.n_packets)]






