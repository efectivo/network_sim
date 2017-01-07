class Algo(object):
    def __init__(self, services):
        self.services = services
        self.is_distributed = None

    def run(self):
        if self.is_distributed:
            for node in self.services.nodes.values():
                self.run_distributed(node)
        else:
            self.run_centralized()

    def run_distributed(self, node):
        pass

    def run_centralized(self):
        pass


# This is a distributed version that send a packet only if the neighbor is empty at the moment
class PassIfEmpty(Algo):
    def __init__(self, services):
        Algo.__init__(self, services)
        self.is_distributed = True

    def run_distributed(self, node):
        for next_node_name, buf in node.buffers.iteritems():
            next_node = self.services.nodes[next_node_name]
            if len(buf) and next_node.curr_total_packets == 0:
                node.send(next_node_name, len(buf))


# Send a packet if the buffer is not empty
class Greedy(Algo):
    def __init__(self, services):
        Algo.__init__(self, services)
        self.is_distributed = True

    def run_distributed(self, node):
        for next_node_name, buf in node.buffers.iteritems():
            if len(buf) == 0:
                continue
            node.send(next_node_name, len(buf))


# Send a packet if the next buffer size is smaller
class DownHill(Algo):
    def __init__(self, services):
        Algo.__init__(self, services)
        self.is_distributed = True

    def run_distributed(self, node):
        to_send = {}
        for next_node_name, buf in node.buffers.iteritems():
            if len(buf) > self.services.nodes[next_node_name].curr_total_packets:
                to_send[next_node_name] = len(buf)

        for next_node_name, buf_len in to_send.iteritems():
            node.send(next_node_name, buf_len)


# Send a packet if the next buffer size is smaller
class OddEven(Algo):
    def __init__(self, services):
        Algo.__init__(self, services)
        self.is_distributed = True

    def run_distributed(self, node):
        to_send = {}
        for next_node_name, buf in node.buffers.iteritems():
            buf_len = len(buf)
            if buf_len == 0:
                continue
            next_node_buf_len = self.services.nodes[next_node_name].curr_total_packets
            if buf_len > next_node_buf_len or buf_len == next_node_buf_len and (buf_len % 2) == 1:
                to_send[next_node_name] = len(buf)

        for next_node_name, buf_len in to_send.iteritems():
            node.send(next_node_name, buf_len)



