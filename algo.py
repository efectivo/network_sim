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

        for node in self.services.nodes.values():
            node.send()

    def run_distributed(self, node):
        pass

    def run_centralized(self):
        pass


class PassIfEmpty(Algo):
    """
    This is a distributed version that send a packet only if the neighbor is empty at the moment
    """
    def __init__(self, services):
        Algo.__init__(self, services)
        self.is_distributed = True

    def run_distributed(self, node):
        for next_node_name, buf in node.buffers.iteritems():
            next_node = self.services.nodes[next_node_name]
            if buf.qsize() > 0 and next_node.current_total_packets == 0:
                node.prepare_packets_for_send(next_node_name)

