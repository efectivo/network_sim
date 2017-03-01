import collections
import logging

class Packet(object):
    next_packet_id = 0
    def __init__(self, policy_name, route, curr_cycle):
        self.policy_name = policy_name
        self.route = route
        self.invoke_cycle = curr_cycle
        self.curr_hop = 0
        self.packet_id = Packet.next_packet_id
        Packet.next_packet_id += 1

    def get_next_hop(self):
        if self.curr_hop == len(self.route):
            return None
        rv = self.route[self.curr_hop]
        self.curr_hop += 1
        return rv

    def __repr__(self):
        return '({},{}):{}'.format(self.packet_id, self.invoke_cycle, self.route)


class Node(object):
    def __init__(self, name, services, buffer_type):
        self.name = name
        self.services = services
        self.buffers = collections.defaultdict(buffer_type)
        self.unit_logger = logging.getLogger('node_{}'.format(name))

        self.curr_total_packets = 0
        self.curr_max_buffer_size = 0
        self.received_packets = collections.defaultdict(list)

    def set_connected_nodes(self):
        self.parents_name = self.services.net.predecessors(self.name)
        self.parents = [self.services.nodes[x] for x in self.parents_name]

        self.children_name = self.services.net.successors(self.name)
        self.children = [self.services.nodes[x] for x in self.children_name]

    def __repr__(self):
        return str(self.name)

    def receive(self, packet):
        next_node = packet.get_next_hop()

        # Packet has reached destination
        if next_node is None:
            self.services.reporter.packet_received(packet)
            return

        # Received packets are queued, so they won't sent again in this cycle
        self.received_packets[next_node].append(packet)

    def cycle_end(self):
        # Update the buffers with the received packets
        for next_node, packets in self.received_packets.iteritems():
            buf = self.buffers[next_node]
            for packet in packets:
                self.unit_logger.debug(packet)
                buf.insert(packet)
            self.curr_total_packets += len(packets)
        self.received_packets = collections.defaultdict(list)

        # Update statistics
        buffers_size = [len(buf) for buf in self.buffers.values()]
        if buffers_size:
            self.curr_max_buffer_size = max(buffers_size)
        else:
            self.curr_max_buffer_size = 0
        self.services.reporter.update_buffer_size(self.name, self.curr_max_buffer_size)

    # Send count packets to next node, by default send as much as possible
    def send(self, next_node_name, count=1e10):
        edge_data = self.services.net.get_edge_data(self.name, next_node_name)
        cap = edge_data['cap'] if 'cap' in edge_data else 1
        buf = self.buffers[next_node_name]
        count = min(cap, len(buf), count)
        for i in xrange(count):
            packet = buf.extract()
            self.curr_total_packets -= 1
            next_node = self.services.nodes[next_node_name]
            next_node.receive(packet)

