import units
import policy
import algo
import networkx as nx
import matplotlib.pyplot as plt
import random


class Sim(object):
    """
    The main class for configuring and running the simulation.
    """
    def __init__(self, alg_type, net, routes, policy_list, cycles=50, verbose=False):
        self.algo = alg_type(self)
        self.net = net
        self.routes = routes
        self.policy = policy_list
        self.cycle_number = cycles
        self.verbose = verbose
        self.reporter = units.Reporter(self)
        self.nodes = {}
        self.curr_cycle = 0

        for node_name in net.nodes():
            node = units.Node(node_name, self)
            node.set_route(routes[node_name])
            self.nodes[node_name] = node

        for node_name, policy in policy_list:
            node = self.nodes[node_name]
            node.add_policy(policy)

    # The cycle has two phases:
    # 1. Each router invokes packets according to its policies
    # 2. Call the algo for packet routing
    def run_cycle(self):
        for node in self.nodes.values():
            node.invoke_packets()

        if self.verbose:
            self.print_state()

        self.algo.run()

        for node in self.nodes.values():
            node.cycle_end()
        self.reporter.cycle_end()

    # The main loop
    def run(self):
        while self.curr_cycle < self.cycle_number:
            self.run_cycle()
            self.curr_cycle += 1

        self.reporter.print_result()
        self.print_state()

    def print_state(self):
        print 'state in cycle: ', self.curr_cycle
        for node in self.nodes.itervalues():
            node.print_state()


def predecessor_to_routing_table(pd_for_node, node_name):
    routing_table = {}
    nodes = pd_for_node.keys()
    while nodes:
        next_nodes = []
        for node in nodes:
            adj_node = pd_for_node[node]
            if adj_node == node_name:
                routing_table[node] = node
            elif adj_node in routing_table.keys():
                routing_table[node] = routing_table[adj_node]
            else:
                next_nodes.append(node)
        nodes = next_nodes
    return routing_table


if __name__ == '__main__':
    random.seed(0)

    # Create simulation
    net = nx.path_graph(4)
    net.get_edge_data(0, 1)['cap'] = 3

    predecessor_dict = nx.floyd_warshall_predecessor_and_distance(net)[0]
    routes = {}
    for k, v in predecessor_dict.iteritems():
        routes[k] = predecessor_to_routing_table(v, k)

    policy = [(0, policy.SendEachCycleTo(3))]
    cycles = 100
    verbose = False

    if False:
        nx.draw(net)
        plt.show()

    s = Sim(algo.PassIfEmpty, net, routes, policy, cycles, verbose)
    s.run()
