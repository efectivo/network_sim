import matplotlib.pyplot as plt
import pandas as pd
import collections
import logging
import networkx as nx


# This reporter show only high level statistics in order to compare different tests
class TestResultsSummary(object):
    def __init__(self):
        self.debugging = False
        self.animating = False
        self.test = None

        self.total_packets_sent = 0
        self.total_packets_recv = 0
        self.total_delay = 0
        self.curr_max_buffer_size = 0
        self.curr_max_packet_delay = 0

        self.total_time_to_delivery = 0
        self.total_route_len = 0
        self.max_delay_factor = 0
        self.average_delay_factor = 0

        self.max_buffer_size_hist = []

    def is_debugging(self):
        return self.debugging

    def get_num_recv_packets(self):
        return self.total_packets_recv

    def init(self, test):
        self.test = test
        self.verbose = test.env.verbose
        self.invoke_logger = logging.getLogger('{}_invoke'.format(test.name))
        self.receive_logger = logging.getLogger('{}_receive'.format(test.name))
        self.result_logger = logging.getLogger('{}_results'.format(test.name))

    # Invocation is similar to all reporter
    def packets_invoked(self, packets):
        self.total_packets_sent += len(packets)
        if self.verbose:
            for packet in packets:
                self.invoke_logger.debug(packet.route)

    def packet_received(self, packet):
        self.total_packets_recv += 1
        time_to_delivery = self.test.env.curr_cycle - packet.invoke_cycle
        route_length = len(packet.route) - 1
        delay_factor = 1. * time_to_delivery / route_length

        self.total_time_to_delivery += time_to_delivery
        self.total_route_len += route_length
        self.max_delay_factor = max(self.max_delay_factor, delay_factor)

        max_packet_delay = self.test.env.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        self.curr_max_packet_delay = max(max_packet_delay, self.curr_max_packet_delay)
        self.total_delay += max_packet_delay
        self.receive_logger.debug(packet)

    def update_buffer_size(self, name, curr_max_buffer_size):
        self.curr_max_buffer_size = max(self.curr_max_buffer_size, curr_max_buffer_size)

        self.max_buffer_size_hist.append(curr_max_buffer_size)

    def finalize(self):
        self.max_packet_delay = self.curr_max_packet_delay
        self.max_buffer_size = self.curr_max_buffer_size

        self.result_logger.info('Total sent: {}'.format(self.total_packets_sent))
        self.result_logger.info('Total recv: {}'.format(self.total_packets_recv))

        self.average_packet_delay = 0
        if self.total_packets_recv > 0:
            self.average_packet_delay = 1. * self.total_delay / self.total_packets_recv
            self.result_logger.info('Average packet delay: {}'.format(self.average_packet_delay))

        self.result_logger.info('Max packet delay: {}'.format(self.curr_max_packet_delay))
        self.result_logger.info('Max buffer size: {}'.format(self.max_buffer_size))

        self.average_delay_factor = 1. * self.total_time_to_delivery / self.total_route_len
        self.result_logger.info('Max delay factor: {}'.format(self.max_delay_factor))
        self.result_logger.info('Average delay factor: {}'.format(self.average_delay_factor))

    def cycle_end(self):
        pass


class TestResultsHistory(TestResultsSummary):
    def init(self, test):
        TestResultsSummary.init(self, test)
        self.max_buffer_size_per_cycle = [0] * (self.test.env.cycle_number * 2)

    def update_buffer_size(self, name, curr_max_buffer_size):
        TestResultsSummary.update_buffer_size(self, name, curr_max_buffer_size)
        curr_cycle = self.test.env.curr_cycle
        self.max_buffer_size_per_cycle[curr_cycle] = max(self.max_buffer_size_per_cycle[curr_cycle], curr_max_buffer_size)
