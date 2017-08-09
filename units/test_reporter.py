import matplotlib.pyplot as plt
import pandas as pd
import collections
import logging
import networkx as nx
import json


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
        self.total_max_buffer_size = 0
        self.cycles = 0


    def is_debugging(self):
        return self.debugging

    def init(self, test):
        self.test = test
        self.network = test.network
        self.logger = logging.getLogger('test')

    def start_cycle(self, cycle):
        self.curr_cycle = cycle

    def packet_invoked(self, packet):
        self.total_packets_sent += 1

    def packet_forwarded(self, dest, src, packet):
        pass

    def packet_received(self, packet):
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

    def cycle_end(self):
        cycle_max_buffer_size = 0
        for n1, n2 in self.network.edges_iter():
            buf_size = len(self.network[n1][n2]['buf'])
            cycle_max_buffer_size = max(cycle_max_buffer_size, buf_size)

        self.total_max_buffer_size += cycle_max_buffer_size
        self.cycles += 1
        self.curr_max_buffer_size = max(self.curr_max_buffer_size, cycle_max_buffer_size)

    def test_finished(self, test_time):
        self.test_time = test_time

    def finalize(self):
        self.max_packet_delay = self.curr_max_packet_delay
        self.max_buffer_size = self.curr_max_buffer_size

        self.average_max_buffer_size = 1. * self.total_max_buffer_size / self.cycles

        self.logger.info('Test have finished. Total seconds: {}'.format(self.test_time.total_seconds()))
        self.logger.info('Total sent: {}'.format(self.total_packets_sent))
        self.logger.info('Total recv: {}'.format(self.total_packets_recv))

        self.average_packet_delay = 0
        if self.total_packets_recv > 0:
            self.average_packet_delay = 1. * self.total_delay / self.total_packets_recv
            self.logger.info('Average packet delay: {}'.format(self.average_packet_delay))

        self.logger.info('Max packet delay: {}'.format(self.max_packet_delay))
        self.logger.info('Max buffer size: {}'.format(self.max_buffer_size))
        self.logger.info('Average max buffer size: {}'.format(self.average_max_buffer_size))

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
        self.edge_dict = {}
        self.d = {}

    def init(self, test):
        TestResultsSummary.init(self, test)

        self.d = {}
        self.d['nodes'] = []
        for n, node in enumerate(self.network.nodes()):
            node_dict = {}
            node_dict['id'] = n
            node_dict['label'] = str(n)
            self.d['nodes'].append(node_dict)

        n = 0
        # {'id': 0, 'from': 0, 'to': 0, 'arrows': 'to'},
        self.d['edges'] = []
        for src, tmp in self.network.edge.iteritems():
            for dest, e in tmp.iteritems():
                edge_dict = {}
                edge_dict['id'] = n
                #edge_dict['label'] = str(n)
                edge_dict['from'] = src
                edge_dict['to'] = dest
                edge_dict['cap'] = e['cap']
                self.d['edges'].append(edge_dict)
                self.edge_dict[src, dest] = n
                n += 1

        #self.d['test_name'] = self.test.name
        self.d['packets'] = {}
        self.d['cycles'] = []

        # self.f.write('NEW,CYCLE_NUM\n')
        # self.f.write('INV,PACKET_ID,ROUTE\n')
        # self.f.write('FWD,PACKET_ID,SRC,DEST\n')

    def start_cycle(self, cycle):
        TestResultsSummary.start_cycle(self, cycle)
        self.curr_cycle_events = []
        self.d['cycles'].append(self.curr_cycle_events)

    def packet_invoked(self, packet):
        TestResultsSummary.packet_invoked(self, packet)
        self.d['packets'][packet.packet_id] = {'route':packet.route, 'invoke':packet.invoke_cycle}
        dest = packet.route[0]
        v = packet.packet_id, -1, -1, dest, packet.route.index(dest), len(packet.route)
        self.curr_cycle_events.append(v)

    def packet_forwarded(self, dest, src, packet):
        TestResultsSummary.packet_forwarded(self, dest, src, packet)
        v = packet.packet_id, self.edge_dict[src, dest], src, dest, packet.route.index(dest), len(packet.route)
        self.curr_cycle_events.append(v)

    # def packet_received(self, packet):
    #     TestResultsSummary.packet_received(self, packet)
    #     v = packet.packet_id, -1, packet.route[-1], -1
    #     self.curr_cycle_events.append(v)

    def finalize(self):
        TestResultsSummary.finalize(self)
        json.dump(self.d, self.f)
        self.f.close()
