import units
import reporter
import logging
import copy


# General configuration for the simulation, define the common modules
class SimulationConfig:
    def __init__(self, net, policy_list, cycle_number=50, log_level=logging.INFO):
        self.net = net
        self.policy_list = policy_list
        self.cycle_number = cycle_number
        self.log_level = log_level


# Test object, hold the state of a specific test (buffers and algorithm)
class Test(object):
    def __init__(self, name, algo, buffer_type, rep=None):
        self.name = name
        self.algo = algo
        self.buffer_type = buffer_type
        self.nodes = {}
        if rep is None:
            rep = reporter.TestResultsSummary()
        self.reporter = rep
        self.reporter.init(self)
        self.sim = None
        self.net = None

    # Initialize the network topology
    def init(self, sim):
        self.sim = sim
        self.net = sim.net

        for node_name in self.net.nodes():
            node = units.Node(node_name, self, self.buffer_type)
            self.nodes[node_name] = node

        for node in self.nodes.itervalues():
            node.set_connected_nodes()

        self.algo.init(self)

    # Run one cycle
    def run(self, packets):
        self.reporter.packets_invoked(packets)

        for packet in packets:
            node_name = packet.get_next_hop()
            node = self.nodes[node_name]
            node.receive(packet)

#            self.reporter.packet_delivery.append(
#                (-1, node_name, packet.packet_id,
#                 self.sim.curr_cycle))


        self.algo.run()

        # Update units
        for node in self.nodes.values():
            node.cycle_end()

        self.reporter.cycle_end()

    def finalize(self):
        self.reporter.finalize()


# The main class for configuring and running the simulation.
class Sim(object):
    def __init__(self, sim_config, tests):
        self.net = sim_config.net
        self.policy_list = sim_config.policy_list
        self.cycle_number = sim_config.cycle_number
        self.curr_cycle = 0
        logging.basicConfig(level=sim_config.log_level)
        self.logger = logging.getLogger('sim')
        self.verbose = sim_config.log_level == logging.DEBUG

        self.tests = tests
        self.debugging = False
        for test in self.tests:
            # Allow only one debugging test
            if test.reporter.debugging:
                assert not self.debugging
                self.debugging = True
            test.init(self)

    # Invoke packets according to injection policy to all tests
    def invoke_packets(self):
        packets = []
        for p in self.policy_list:
            packets += p.invoke(self.curr_cycle)
        return packets

    def run(self):
        while self.curr_cycle < self.cycle_number:
            self.logger.debug(self.curr_cycle)

            # Invoke new packets
            packets = self.invoke_packets()

            # Route existing packets per test
            for test in self.tests:
                packets_copy = copy.deepcopy(packets)
                test.run(packets_copy)

            self.curr_cycle += 1

        for test in self.tests:
            test.finalize()

