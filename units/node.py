import collections
import logging

class Node(object):
    def __init__(self, name, reporter, buffer_type):
        self.name = name
        self.reporter = reporter
        self.buffer_type = buffer_type

        self.buffers = {}
        self.nodes = None

        self.node_logger = logging.getLogger('{}_node_{}'.format(self.reporter.test.name, name))
        self.curr_total_packets = 0
        self.curr_max_buffer_size = 0
        self.received_packets = collections.defaultdict(list)

    # Cache relevant attributes
    def update_topology(self, network, nodes):
        self.nodes = nodes
        self.parents_name = network.predecessors(self.name)
        self.parents = [nodes[x] for x in self.parents_name]

        self.edge_capacity_per_parent = {}
        for parent_name in self.parents_name:
            edge_data = network.edge[parent_name][self.name]
            cap_per_parent = edge_data['cap'] if 'cap' in edge_data else 1
            self.edge_capacity_per_parent[parent_name] = cap_per_parent

        self.children_name = network.successors(self.name)
        self.children = [nodes[x] for x in self.children_name]

        self.edge_capacity_per_child = {}
        for child_name in self.children_name:
            edge_data = network.edge[self.name][child_name]
            cap_per_child = edge_data['cap'] if 'cap' in edge_data else 1
            self.edge_capacity_per_child[child_name] = cap_per_child

        for child_name in self.children_name:
            self.buffers[child_name] = self.buffer_type()

    def receive(self, packet):
        packet.packet_received()
        next_node_name = packet.get_next_hop()

        # Packet has reached destination
        if next_node_name is None:
            self.reporter.packet_received(packet)
            return

        self.node_logger.debug(packet)
        # Received packets are queued, so they won't sent again in this cycle
        self.received_packets[next_node_name].append(packet)

    def cycle_end(self):
        # Update the buffers with the received packets
        for next_node, packets in self.received_packets.iteritems():
            buf = self.buffers[next_node]
            for packet in packets:
                buf.insert(packet)
            self.curr_total_packets += len(packets)
        self.received_packets = collections.defaultdict(list)

        # Update statistics
        buffers_size = [len(buf) for buf in self.buffers.values()]
        if buffers_size:
            self.curr_max_buffer_size = max(buffers_size)
        else:
            self.curr_max_buffer_size = 0
        self.reporter.update_buffer_size(self.name, self.curr_max_buffer_size)

    # Send count packets to next node, by default send as much as possible
    def send(self, next_node_name, count, **kvdict):
        buf = self.buffers[next_node_name]
        for i in xrange(count):
            packet = buf.extract(**kvdict)
            self.curr_total_packets -= 1
            next_node = self.nodes[next_node_name]
            next_node.receive(packet)

    def __repr__(self):
        return 'N' + str(self.name)
