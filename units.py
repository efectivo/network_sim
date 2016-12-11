import Queue
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
        self.total_hops = 0
        self.total_cycles = 0
        self.max_size_per_cycle = []

    def print_result(self):
        print 'Total sent: {}'.format(self.total_packets_sent)
        print 'Total recv: {}'.format(self.total_packets_recv)
        print 'Avg hops: {}'.format(self.total_hops / self.total_packets_recv)
        plt.plot(self.max_size_per_cycle); plt.title('max buffer size per cycle')
        plt.show()

    def packet_received(self, packet):
        self.total_packets_recv += 1
        self.total_hops += packet.hops
        self.total_cycles += self.services.curr_cycle - packet.invoke_cycle

    def cycle_end(self):
        max_size = max([node.curr_max_buffer_size for node in self.services.nodes.values()])
        self.max_size_per_cycle.append(max_size)

class Packet(object):
    """
    The packet structure, define it's source and destination and debug info
    """
    next_packet_id = 0

    def __init__(self, dst):
        self.dst = dst
        self.id = self.next_packet_id
        self.next_packet_id += 1
        self.hops = 0
        self.invoke_cycle = 0


class Node(object):
    """
    The node in the graph.
    Has route table to all other nodes, and buffer per each neighbor.
    """
    def __init__(self, name, services):
        self.name = name
        self.services = services
        self.routing_table = {}
        self.current_total_packets = 0
        self.buffers = collections.defaultdict(Queue.Queue)
        self.policies = []
        self.packets_to_send_in_this_cycle = {}
        self.curr_max_buffer_size = 0

    def __repr__(self):
        return 'Node: {}'.format(self.name)

    def add_policy(self, policy):
        self.policies.append(policy)

    def set_route(self, route):
        self.routing_table = route
        for node in set(route.itervalues()):
            _ = self.buffers[node]

    def invoke_packets(self):
        for policy in self.policies:
            packets = policy.invoke()
            self.services.reporter.total_packets_sent += len(packets)
            for packet in packets:
                next_node = self.routing_table[packet.dst]
                buf = self.buffers[next_node]
                buf.put(packet)

    def route(self, packet):
        packet.hops += 1

        # Packet has reached destination
        if self.name == packet.dst:
            self.services.reporter.packet_received(packet)
            return

        next_node = self.routing_table[packet.dst]
        buf = self.buffers[next_node]
        buf.put(packet)
        self.current_total_packets += 1

    def cycle_end(self):
        self.curr_max_buffer_size = max([buf.qsize() for buf in self.buffers.values()])

    # Send the front packet in the queue to this neighbor -
    # Doesn't send yet so the current state won't change in a distributed algorithm
    def prepare_packets_for_send(self, next_node):
        edge_data = self.services.net.get_edge_data(self.name, next_node)
        cap = edge_data['cap'] if 'cap' in edge_data else 1
        buf = self.buffers[next_node]
        packet_count_to_send = min(cap, buf.qsize())
        self.packets_to_send_in_this_cycle[next_node] = (buf, packet_count_to_send)

    def send(self):
        for next_node_name, (buf, packet_count_to_send) in self.packets_to_send_in_this_cycle.iteritems():
            for i in xrange(packet_count_to_send):
                next_node = self.services.nodes[next_node_name]
                packet = buf.get()
                next_node.route(packet)
                self.current_total_packets -= 1
        self.packets_to_send_in_this_cycle = {}

    def print_state(self):
        for node, buf in self.buffers.iteritems():
            print '{}->{}: {}'.format(self, node, buf.qsize())

