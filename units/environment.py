import logging
import copy
import datetime
import networkx as nx

# General configuration for the simulation, define the common modules
class EnvironmentSetup:
    def __init__(self, network, pattern, cycle_number=50, log_level=logging.INFO):
        self.network = network
        self.pattern = pattern
        self.cycle_number = cycle_number
        self.log_level = log_level

class Environment(object):
    def __init__(self, setup, tests):
        assert len(tests)>0, 'Enter at least one test'
        assert type(setup.network) == nx.DiGraph, 'Network should be a directed graph'

        # The common part
        self.network = setup.network
        # Set default capacity values to 1
        for n1, n2 in self.network.edges_iter():
            edge_attr = self.network[n1][n2]
            if 'cap' not in edge_attr:
                edge_attr['cap'] = 1

        self.pattern = setup.pattern
        self.cycle_number = setup.cycle_number
        logging.basicConfig(level=setup.log_level)

        # Give the tests access to the common parts
        name_set = set()
        self.tests = tests
        assert sum([test.reporter.is_debugging() for test in tests]) <= 1, 'Cannot debug more than one test'
        for test in self.tests:
            #assert test.name not in self.tests, 'Tests name should be unique'
            #name_set.add(test.name)

            test.init(self)

    def run(self):
        start = datetime.datetime.now()

        for curr_cycle in xrange(self.cycle_number):
            # Create the packets that should be injected in this cycle
            packets = self.pattern.invoke(curr_cycle)

            # Now run each protocol independently
            for test in self.tests:
                test.reporter.start_cycle(curr_cycle)
                test.run_communication_step()
                test.run_forwarding_step()
                if len(packets) > 0:
                    test.run_injection_step(copy.deepcopy(packets))
                test.run_reporting_step()

        for test in self.tests:
            test.reporter.test_finished(datetime.datetime.now() - start)
            test.finalize()

