import logging
import copy
import datetime
import networkx as nx

# General configuration for the simulation, define the common modules
class EnvironmentSetup:
    def __init__(self, network, patterns, cycle_number=50, log_level=logging.INFO):
        self.network = network
        self.patterns = patterns
        self.cycle_number = cycle_number
        self.log_level = log_level

class Environment(object):
    def __init__(self, setup, tests):
        assert len(tests)>0, 'Enter at least one test'
        assert type(setup.network) == nx.DiGraph, 'Network should be a directed graph'
        assert len(setup.patterns) > 0, 'Enter at least one injection pattern'

        # The common part
        self.network = setup.network
        # Set default capacity values to 1
        for n1, n2 in self.network.edges_iter():
            edge_attr = self.network[n1][n2]
            if 'cap' not in edge_attr:
                edge_attr['cap'] = 1

        self.patterns = setup.patterns
        self.cycle_number = setup.cycle_number
        logging.basicConfig(level=setup.log_level)
        self.curr_cycle = 0

        # Give the tests access to the common parts
        name_set = set()
        self.tests = tests
        assert sum([test.reporter.is_debugging() for test in tests]) <= 1, 'Cannot debug more than one test'
        for test in self.tests:
            assert test.name not in self.tests, 'Tests name should be unique'
            name_set.add(test.name)

            test.init(self)

    def run(self):
        start = datetime.datetime.now()

        finished_tests = set()
        num_sent_packets = 0
        inject_packets = True

        test_num = len(self.tests)
        while len(finished_tests) < test_num:
            if self.curr_cycle == self.cycle_number:
                inject_packets = False

            packets = []
            if inject_packets:
                # Create the packets that should be injected in this cycle
                packets = sum([p.invoke(self.curr_cycle) for p in self.patterns], [])
                num_sent_packets += len(packets)

            # Now run each protocol independently
            for test in self.tests:
                test.reporter.start_cycle(self.curr_cycle)
                test.run_communication_step()
                test.run_forwarding_step()
                if len(packets) > 0:
                    test.run_injection_step(copy.deepcopy(packets))
                test.run_reporting_step()

                if not inject_packets and test not in finished_tests:
                    if test.reporter.get_num_recv_packets() == num_sent_packets:
                        test.reporter.test_finished(datetime.datetime.now() - start)
                        finished_tests.add(test)

            self.curr_cycle += 1

        for test in self.tests:
            test.finalize()

