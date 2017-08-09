import forwarding_buffer
from units import node

class ForwardingProtocol(object):
    def __init__(self):
        self.scheduling_policy = None
        self.test = None
        self.network = None

    def set_scheduling_policy(self, p):
        self.scheduling_policy = p

    def init(self, test):
        self.test = test
        self.network = self.test.network

    def create_node(self, node_name, network):
        return node.Node(node_name, network)

    def create_buffer(self):
        return self.scheduling_policy()

    def run_communication_step(self):
        pass

    def run_forwarding_step(self):
        pass


