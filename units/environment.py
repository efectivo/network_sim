import logging
import copy

# General configuration for the simulation, define the common modules
class EnvironmentSetup:
    def __init__(self, network, patterns, cycle_number=50, log_level=logging.INFO):
        self.network = network
        self.patterns = patterns
        self.cycle_number = cycle_number
        self.log_level = log_level

class Environment(object):
    def __init__(self, setup, tests):
        # The common part
        self.network = setup.network
        self.patterns = setup.patterns
        self.cycle_number = setup.cycle_number
        logging.basicConfig(level=setup.log_level)
        self.logger = logging.getLogger('env')
        self.verbose = setup.log_level == logging.DEBUG
        self.curr_cycle = 0

        # Give the tests access to the common parts
        self.tests = tests
        assert sum([test.reporter.is_debugging() for test in tests]) <= 1
        for test in self.tests:
            test.init(self)

    def run(self):
        finished_tests = set()
        num_sent_packets = 0
        inject_packets = True
        test_num = len(self.tests)

        while len(finished_tests) < test_num:
            if self.curr_cycle == self.cycle_number:
                inject_packets = False

            self.logger.debug(self.curr_cycle)

            packets = []
            if inject_packets:
                # Create the packets that should be injected in this cycle
                packets = sum([p.invoke(self.curr_cycle) for p in self.patterns], [])
                num_sent_packets += len(packets)

            # Now run each protocol independently
            for test in self.tests:
                test.run_communication_step()
                test.run_forwarding_step()
                if len(packets) > 0:
                    test.run_injection_step(copy.deepcopy(packets))
                test.run_reporting_step()

                if not inject_packets and test not in finished_tests:
                    if test.reporter.get_num_recv_packets() == num_sent_packets:
                        finished_tests.add(test)

            self.curr_cycle += 1

        for test in self.tests:
            test.finalize()

