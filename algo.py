import random

# The algorithm runs independently on each node
DISTRIBUTED = 0

# Runs over the entire graph
CENTRALIZED = 1

# For directed graphs only, run on a sibling list per common child
PER_CHILD = 2


class Algo(object):
    def __init__(self, run_type):
        self.run_type = run_type

    def init(self, services):
        self.services = services

        # Run once per child and his parents, create the static list here
        if self.run_type == PER_CHILD:
            self.run = self._run_per_child
            self.nodes_iter = []
            for node_name in services.net:
                node = self.services.nodes[node_name]
                parents_name = services.net.predecessors(node_name)
                if parents_name:
                    parents = [self.services.nodes[x] for x in parents_name]
                    self.nodes_iter.append((node, parents))

        elif self.run_type == CENTRALIZED:
            self.run = self.run_centralized

        # Distrubuted, run once per node
        elif self.run_type == DISTRIBUTED:
            self.run = self._run_distributed
            self.nodes = self.services.nodes.values()

    def _run_per_child(self):
        self.to_send = {}
        # Calculate first what need to be sent, in order not to interfere with other nodes decisions
        for node, parents in self.nodes_iter:
            self.run_per_child(node, parents)
        for (node, next_node_name), buf_len in self.to_send.iteritems():
            node.send(next_node_name, buf_len)

    def _run_distributed(self):
        self.to_send = {}
        for node in self.nodes:
            self.run_distributed(node)
        for (node, next_node_name), buf_len in self.to_send.iteritems():
            node.send(next_node_name, buf_len)


# This is a distributed version that send a packet only if the neighbor is empty at the moment
class PassIfEmpty(Algo):
    def __init__(self):
        Algo.__init__(self, DISTRIBUTED)

    def run_distributed(self, node):
        for next_node_name, buf in node.buffers.iteritems():
            next_node = self.services.nodes[next_node_name]
            if len(buf) and next_node.curr_total_packets == 0:
                node.send(next_node_name, len(buf))


# Send a packet if the buffer is not empty
class Greedy(Algo):
    def __init__(self):
        Algo.__init__(self, DISTRIBUTED)

    def run_distributed(self, node):
        for next_node_name, buf in node.buffers.iteritems():
            if len(buf) == 0:
                continue
            self.to_send[node, next_node_name] = len(buf)


# Send a packet if the next buffer size is smaller
class DownHill(Algo):
    def __init__(self, use_odd_even):
        Algo.__init__(self, PER_CHILD)
        self.use_odd_even = use_odd_even

    def run_per_child(self, node, parents):
        curr_max = 0
        curr_count = 0
        max_parent = None
        # Go over the parents and choose the one with the largest buffer
        for parent in parents:
            buf_size = len(parent.buffers[node.name])
            if buf_size > curr_max:
                curr_count = 1
                max_parent = parent
                curr_max = buf_size
            # In case of equality, choose randomly
            elif buf_size > 0 and buf_size == curr_max:
                curr_count += 1
                if random.random() < 1./curr_count:
                    max_parent = parent

        if not max_parent:
            return

        next_node_buf_len = node.curr_total_packets
        # Forward the packets odd even downhill
        if curr_max > next_node_buf_len or self.use_odd_even and curr_max == next_node_buf_len and (curr_max % 2) == 1:
            self.to_send[max_parent, node.name] = curr_max

