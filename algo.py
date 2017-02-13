import random

class Algo(object):
    def init(self, services):
        self.services = services

    def run(self):
        self.to_send = {}
        # Calculate first what need to be sent, in order not to interfere with other nodes decisions
        for node in self.services.nodes.itervalues():
            self.run_node(node)
        for (node, next_node_name), buf_len in self.to_send.iteritems():
            node.send(next_node_name, buf_len)


# Send a packet if the buffer is not empty
class Greedy(Algo):
    def run_node(self, node):
        for parent in node.parents:
            buf = parent.buffers[node.name]
            if len(buf) == 0:
                continue
            self.to_send[parent, node.name] = len(buf)


# Send a packet if the next buffer size is smaller
class DownHill(Algo):
    def __init__(self, use_odd_even):
        self.use_odd_even = use_odd_even

    def run_node(self, node):
        curr_max = 0
        curr_count = 0
        max_parent = None
        # Go over the parents and choose the one with the largest buffer
        for parent in node.parents:
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

