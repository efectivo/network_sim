import forwarding_buffer
from units import node

class ForwardingProtocol(object):
    def __init__(self, buffer_type=forwarding_buffer.LongestInSystem):
        self.buffer_type = buffer_type
        self.nodes = None

    def set_env(self, test):
        self.test = test
        self.nodes = test.nodes

    def init(self):
        pass

    # Factory method can be override
    def create_node(self, node_name):
        return node.Node(node_name, self.nodes, self.test.reporter, self.buffer_type)

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        pass


