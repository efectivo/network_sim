import forwarding_buffer
from units import node

class ForwardingProtocol(object):
    def __init__(self, buffer_type=forwarding_buffer.LongestInSystem):
        self.buffer_type = buffer_type
        self.test = None
        self.network = None

    def init(self, test):
        self.test = test
        self.network = self.test.network

    def create_node(self, node_name, network):
        return node.Node(node_name, network)

    def create_buffer(self):
        return self.buffer_type()

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        pass


