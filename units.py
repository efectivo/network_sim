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

    def get_next_hop(self, update=True):
        if self.curr_hop == len(self.route):
            return None
        rv = self.route[self.curr_hop]
        if update:
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

        self.edge_capacity_per_parent = {}
        for parent_name in self.parents_name:
            edge_data = self.services.net.edge[parent_name][self.name]
            cap_per_parent = edge_data['cap'] if 'cap' in edge_data else 1
            self.edge_capacity_per_parent[parent_name] = cap_per_parent

        self.children_name = self.services.net.successors(self.name)
        self.children = [self.services.nodes[x] for x in self.children_name]

        self.edge_capacity_per_child = {}
        for child_name in self.children_name:
            edge_data = self.services.net.edge[self.name][child_name]
            cap_per_child = edge_data['cap'] if 'cap' in edge_data else 1
            self.edge_capacity_per_child[child_name] = cap_per_child

    def __repr__(self):
        return 'N' + str(self.name)

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
        #self.services.reporter.update_buffer(self.name, self.buffers)

    # Send count packets to next node, by default send as much as possible
    def send(self, next_node_name, count=1e10):
        edge_data = self.services.net.get_edge_data(self.name, next_node_name)
        cap = edge_data['cap'] if 'cap' in edge_data else 1
        buf = self.buffers[next_node_name]
        count = min(cap, len(buf), count)
        for i in xrange(count):
            packet = buf.extract()
#            self.services.reporter.packet_delivery.append(
#                (self.name, next_node_name, packet.packet_id,
#                 self.services.sim.curr_cycle))
            self.curr_total_packets -= 1
            next_node = self.services.nodes[next_node_name]
            next_node.receive(packet)


class NodeWithPseudoBuffers(Node):
    def __init__(self, name, services, buffer_type):
        Node.__init__(self, name, services, buffer_type)

        self.buffers = collections.defaultdict(lambda: collections.defaultdict(buffer_type))
        self.received_packets = collections.defaultdict(lambda: collections.defaultdict(list))

    def receive(self, packet):
        next_node = packet.get_next_hop()

        # Packet has reached destination
        if next_node is None:
            self.services.reporter.packet_received(packet)
            return

        two_steps_node = packet.get_next_hop(False)
        if two_steps_node is None:
            two_steps_node = -1

        # Received packets are queued, so they won't sent again in this cycle
        self.received_packets[next_node][two_steps_node].append(packet)

    def cycle_end(self):
        # Update pseudo buffers
        for next_node, pseudo_buffers in self.received_packets.iteritems():
            for two_step_node, packets in pseudo_buffers.iteritems():
                buf = self.buffers[next_node][two_step_node]
                for packet in packets:
                    self.unit_logger.debug(packet)
                    buf.insert(packet)
                self.curr_total_packets += len(packets)
        self.received_packets = collections.defaultdict(lambda: collections.defaultdict(list))

        # Update statistics
        self.curr_max_buffer_size = 0
        for pseudo_buffers in self.buffers.values():
            self.curr_max_buffer_size = sum([len(pseudo_buffer) for pseudo_buffer in pseudo_buffers.values()])

        self.services.reporter.update_buffer_size(self.name, self.curr_max_buffer_size)
        # self.services.reporter.update_buffer(self.name, self.buffers)

    # Extract "count" packet from the pseudo buffer and send it to the next node
    # The send should hold the capacity limit
    def send(self, next_node_name, two_steps_node_name, count=1):
        cap = self.edge_capacity_per_child[next_node_name]
        assert count <= cap
        pseudo_buf = self.buffers[next_node_name][two_steps_node_name]
        for i in xrange(count):
            packet = pseudo_buf.extract()
            assert packet is not None
            next_node = self.services.nodes[next_node_name]
            next_node.receive(packet)
