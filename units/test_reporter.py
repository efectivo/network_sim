import matplotlib.pyplot as plt
import pandas as pd
import collections
import logging
import networkx as nx


# This reporter show only high level statistics in order to compare different tests
class TestResultsSummary(object):
    def __init__(self):
        self.debugging = False
        self.test = None
        self.logger = None
        self.curr_cycle = None

        self.total_packets_sent = 0
        self.total_packets_recv = 0
        self.total_delay = 0
        self.curr_max_buffer_size = 0
        self.curr_max_packet_delay = 0
        self.total_time_to_delivery = 0
        self.total_route_len = 0
        self.max_delay_factor = 0
        self.average_delay_factor = 0

    def is_debugging(self):
        return self.debugging

    def init(self, test):
        self.test = test
        self.network = test.network
        self.logger = logging.getLogger(test.name)

    def start_cycle(self, cycle):
        self.curr_cycle = cycle
        self.logger.debug('NEW_CYCLE: {}'.format(cycle))

    def packet_invoked(self, packet):
        self.logger.debug('PACKET_INVOKED: {}'.format(packet))
        self.total_packets_sent += 1

    def packet_forwarded(self, dest, src, packet):
        self.logger.debug('PACKET_FORWARD: {}=>{}, {}'.format(src, dest, packet))

    def packet_received(self, packet):
        self.logger.debug('PACKET_RECEIVED: {}'.format(packet))

        self.total_packets_recv += 1
        time_to_delivery = self.curr_cycle - packet.invoke_cycle
        route_length = len(packet.route) - 1
        delay_factor = 1. * time_to_delivery / route_length

        self.total_time_to_delivery += time_to_delivery
        self.total_route_len += route_length
        self.max_delay_factor = max(self.max_delay_factor, delay_factor)

        max_packet_delay = self.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        self.curr_max_packet_delay = max(max_packet_delay, self.curr_max_packet_delay)
        self.total_delay += max_packet_delay

    def get_num_recv_packets(self):
        return self.total_packets_recv

    def cycle_end(self):
        for n1, n2 in self.network.edges_iter():
            buf_size = len(self.network[n1][n2]['buf'])
            self.curr_max_buffer_size = max(self.curr_max_buffer_size, buf_size)

    def test_finished(self, test_time):
        self.test_time = test_time

    def finalize(self):
        self.max_packet_delay = self.curr_max_packet_delay
        self.max_buffer_size = self.curr_max_buffer_size

        self.logger.info('Test have finished. Total seconds: {}'.format(self.test_time.total_seconds()))
        self.logger.info('Total sent: {}'.format(self.total_packets_sent))
        self.logger.info('Total recv: {}'.format(self.total_packets_recv))

        self.average_packet_delay = 0
        if self.total_packets_recv > 0:
            self.average_packet_delay = 1. * self.total_delay / self.total_packets_recv
            self.logger.info('Average packet delay: {}'.format(self.average_packet_delay))

        self.logger.info('Max packet delay: {}'.format(self.curr_max_packet_delay))
        self.logger.info('Max buffer size: {}'.format(self.max_buffer_size))

        self.average_delay_factor = 1. * self.total_time_to_delivery / self.total_route_len
        self.logger.info('Max delay factor: {}'.format(self.max_delay_factor))
        self.logger.info('Average delay factor: {}'.format(self.average_delay_factor))


class TestResultsHistory(TestResultsSummary):
    def __init__(self, output_file):
        TestResultsSummary.__init__(self)
        self.stats = {}
        self.output_file = output_file

    def cycle_end(self):
        for n1, n2 in self.network.edges_iter():
            buf_size = len(self.network[n1][n2]['buf'])
            self.curr_max_buffer_size = max(self.curr_max_buffer_size, buf_size)
            self.stats[(n1, n2, self.curr_cycle)] = (buf_size,)

    def finalize(self):
        TestResultsSummary.finalize(self)
        df = pd.DataFrame(self.stats).T
        df.columns = ['BUF'] # Relevant only when there is more than one port
        df.index.names = ['NODE', 'CYCLE']
        if self.output_file.endswith('.csv'):
            df.to_csv(self.output_file)
        else:
            df.to_hdf(self.output_file, 'abc')

class TestResultsLog(TestResultsSummary):
    def __init__(self, output_file):
        TestResultsSummary.__init__(self)
        self.f = open(output_file, 'wt')

    def init(self, test):
        TestResultsSummary.init(self, test)
        self.f.write('# This is an auto-generated file created by TestResultsLog. don\'t edit manually.\n')
        self.f.write('{}\n'.format(self.test.name))
        self.f.write('{}\n'.format(self.network.number_of_edges()))
        nx.write_edgelist(self.network, self.f)
        self.f.write('NEW,CYCLE_NUM\n')
        self.f.write('INV,PACKET_ID,ROUTE\n')
        self.f.write('FWD,PACKET_ID,SRC,DEST\n')

    def start_cycle(self, cycle):
        TestResultsSummary.start_cycle(self, cycle)
        self.f.write('NEW,{}\n'.format(cycle))

    def packet_invoked(self, packet):
        TestResultsSummary.packet_invoked(self, packet)
        self.f.write('INV,{},{}\n'.format(packet.packet_id, '>'.join(map(str, packet.route))))

    def packet_forwarded(self, dest, src, packet):
        TestResultsSummary.packet_forwarded(self, dest, src, packet)
        self.f.write('FWD,{},{},{}\n'.format(packet.packet_id, src, dest))

    def finalize(self):
        TestResultsSummary.finalize(self)
        self.f.close()
