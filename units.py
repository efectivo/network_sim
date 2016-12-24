import collections
import matplotlib.pyplot as plt


class Reporter(object):
    """
    This class collect the statistics and aggregate them.
    Print simulation summary at the end.
    """
    def __init__(self, services):
        self.services = services
        self.total_packets_sent = 0
        self.total_packets_recv = 0
        self.total_cycles = 0
        self.max_size_per_cycle = []
        self.packets = []

    def print_result(self):
        print self.packets
        print 'Total sent: {}'.format(self.total_packets_sent)
        print 'Total recv: {}'.format(self.total_packets_recv)
        print 'Avg cycles: {}'.format(self.total_cycles / self.total_packets_recv)
        plt.plot(self.max_size_per_cycle); plt.title('max buffer size per cycle')
        plt.show()

    def packet_received(self, packet):
        self.total_packets_recv += 1
        self.total_cycles += self.services.curr_cycle - packet.invoke_cycle
        self.packets.append(packet)

    def cycle_end(self):
        max_size = max([node.curr_max_buffer_size for node in self.services.nodes.values()])
        self.max_size_per_cycle.append(max_size)


class Packet(object):
    """
    The packet structure, define it's source and destination and debug info
    """
    next_packet_id = 0

    def __init__(self, pname, route, curr_cycle):
        # self.route[0] == src
        self.route = route
        self.curr_hop = 0
        self.id = Packet.next_packet_id
        self.policy_name = pname
        Packet.next_packet_id += 1
        self.invoke_cycle = curr_cycle

    def next(self):
        self.curr_hop += 1
        if self.curr_hop == len(self.route):
            return None
        return self.route[self.curr_hop]

    def __repr__(self):
        return '{}_{}_{}'.format(self.policy_name, self.invoke_cycle, self.id)


class Node(object):
    """
    The node in the graph.
    Has route table to all other nodes, and buffer per each neighbor.
    """
    def __init__(self, name, services, buffer_type):
        self.name = name
        self.services = services
        self.current_total_packets = 0
        self.buffers = collections.defaultdict(buffer_type)
        self.policies = []

        self.packets_to_send_in_this_cycle = {}
        self.curr_max_buffer_size = 0

    def __repr__(self):
        return 'N' + str(self.name)

    def add_policy(self, policy):
        self.policies.append(policy)

    def invoke_packets(self):
        for policy in self.policies:
            packets = policy.invoke(self.services.curr_cycle)
            self.services.reporter.total_packets_sent += len(packets)
            for packet in packets:
                self.receive(packet)

    def receive(self, packet):
        next_node = packet.next()

        # Packet has reached destination
        if not next_node:
            self.services.reporter.packet_received(packet)
            return

        buf = self.buffers[next_node]
        buf.insert(packet)
        self.current_total_packets += 1

    def cycle_end(self):
        if not len(self.buffers):
            return
        self.curr_max_buffer_size = max([len(buf) for buf in self.buffers.values()])

    # Send the front packet in the queue to this neighbor -
    # Doesn't send yet so the current state won't change in a distributed algorithm
    def prepare_packets_for_send(self, next_node):
        edge_data = self.services.net.get_edge_data(self.name, next_node)
        cap = edge_data['cap'] if 'cap' in edge_data else 1
        buf = self.buffers[next_node]
        packet_count_to_send = min(cap, len(buf))
        self.packets_to_send_in_this_cycle[next_node] = (buf, packet_count_to_send)

    def send(self):
        for next_node_name, (buf, packet_count_to_send) in self.packets_to_send_in_this_cycle.iteritems():
            for i in xrange(packet_count_to_send):
                next_node = self.services.nodes[next_node_name]
                packet = buf.extract()
                self.current_total_packets -= 1
                next_node.receive(packet)
        self.packets_to_send_in_this_cycle = {}

    def print_state(self):
        for node, buf in self.buffers.iteritems():
            print '{}->{}: {}'.format(self, node, len(buf))

