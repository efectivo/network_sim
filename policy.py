import units
import networkx as nx


class Policy(object):
    def __init__(self, src, net):
        self.src = src
        self.net = net

    def invoke(self):
        pass

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
        Policy.__init__(self, src, net)
        self.name = 'sec_{}->{}'.format(src, dst)
        self.all_paths = list(nx.all_simple_paths(net, source=src, target=dst))
        for p in self.all_paths:
            self.update_load(p, 1./len(self.all_paths))
        self.curr_path = 0

    def invoke(self, curr_cycle):
        p = units.Packet(self.name, self.all_paths[self.curr_path], curr_cycle)
        self.curr_path = (self.curr_path + 1) % len(self.all_paths)
        return [p,]
