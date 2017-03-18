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

    def init(self, test):
        self.test = test
        self.invoke_logger = logging.getLogger('invoke_{}'.format(test.name))
        self.receive_logger = logging.getLogger('receive_{}'.format(test.name))
        self.result_logger = logging.getLogger('results_{}'.format(test.name))

    # Invocation is similar to all reporter
    def packets_invoked(self, packets):
        self.total_packets_sent += len(packets)
        if self.test.sim.verbose:
            for packet in packets:
                self.invoke_logger.debug(packet)

    def packet_received(self, packet):
        self.total_packets_recv += 1
        max_packet_delay = self.test.sim.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        self.curr_max_packet_delay = max(max_packet_delay, self.curr_max_packet_delay)
        self.total_delay += max_packet_delay
        self.receive_logger.debug(packet)

    def update_buffer_size(self, name, curr_max_buffer_size):
        self.curr_max_buffer_size = max(self.curr_max_buffer_size, curr_max_buffer_size)

    def finalize(self):
        self.result_logger.info('Total sent: {}'.format(self.total_packets_sent))
        self.result_logger.info('Total recv: {}'.format(self.total_packets_recv))
        self.result_logger.info('Max packet delay: {}'.format(self.curr_max_packet_delay))
        if self.total_packets_recv > 0:
            self.result_logger.info('Average packet delay: {}'.format(1.0*self.total_delay/self.total_packets_recv))
        self.result_logger.info('Max buffer size: {}'.format(self.curr_max_buffer_size))

    def cycle_end(self):
        pass


class TestResultsAnimation(TestResultsSummary):
    def __init__(self):
        TestResultsSummary.__init__(self)
        self.debugging = True
        self.animating = True
        self.fig = None
        self.new_packets = set()

    def cycle_end(self):
        self._animate()
        self.new_packets = set()

    def packets_invoked(self, packets):
        self.total_packets_sent += len(packets)
        if self.test.sim.verbose:
            for packet in packets:
                self.new_packets.add(packet.route[0])
                self.invoke_logger.debug(packet)

    def _animate(self):
        sim = self.test.sim
        if not self.fig:
            self.fig = plt.figure()
            self.pos = nx.spring_layout(sim.net)

        self.fig.clear()
        labels = {}
        node_color = []
        for node_name, node in self.test.nodes.iteritems():
            #labels[node_name] = '({}):{}'.format(node_name, node.curr_total_packets)
            tmp = []
            for k, buf in node.buffers.items():
                for packet in buf.values:
                    tmp.append('{}_{}'.format(packet[1].packet_id, '-'.join(map(str, packet[1].route))))
            labels[node_name] = '({}):{}'.format(node_name, ','.join(tmp))
            node_color.append('r' if node_name in self.new_packets else 'g')

        nx.draw_networkx(sim.net, self.pos, labels=labels,
                         node_size=1600, node_color=node_color,
                         node_shape='s', font_size=15)

        self.fig.suptitle(sim.curr_cycle, fontsize=20)
        self.new_packets = set()
        self.fig.canvas.draw()

        plt.waitforbuttonpress(timeout=-1)


class TestResultsHistory(TestResultsSummary):
    def __init__(self, plot_buffer_state=False):
        TestResultsSummary.__init__(self)
        self.debugging = True

        self.packet_delay = collections.OrderedDict()
        self.stats = {}
        self.buffer_stats = {}
        self.df = None
        self.packet_delay_df = None
        self.plot_buffer_state = plot_buffer_state

        self.packet_delivery = []

    def packet_received(self, packet):
        self.total_packets_recv += 1
        self.packet_delay[str(packet)] = self.test.sim.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        self.receive_logger.debug(packet)

    def update_buffer_size(self, name, curr_max_buffer_size):
        self.stats[(name, self.test.sim.curr_cycle)] = (curr_max_buffer_size,)

    def update_buffer(self, name, buffers):
        out = []
        for k, v in buffers.iteritems():
            if v.values:
                print k, v.values[0][1], str(v.values[0][1])
            out.append('{}@{}'.format(k, ':'.join(v.values)))
        print out
        self.buffer_stats[(name, self.test.sim.curr_cycle)] = '*'.join(out)

    def finalize(self):
        TestResultsSummary.finalize(self)
        df = pd.DataFrame(self.stats).T
        df.columns = ['BUF'] # Relevant only when there is more than one port
        df.index.names = ['NODE', 'CYCLE']
        self.df = df.reset_index()
        self.packet_delay_df = pd.Series(self.packet_delay.values())

        self._plot_graphs()
        if self.plot_buffer_state:
            self._plot_buffer_state()

        delivery_df = pd.DataFrame(self.packet_delivery, columns=['from', 'to', 'pid', 'cycle'])
        delivery_df.to_csv(r'E:\TOAR2\Network\notebooks\results_tmp.csv')

    def _plot_graphs(self):
        df = self.df.groupby('CYCLE').BUF
        df.agg(['max', 'mean']).plot(title='Buffer statistics per node')
        plt.show()

    def _plot_buffer_state(self):
        from mpl_toolkits.mplot3d import Axes3D

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        df = self.df
        ax.bar(df.NODE, df.BUF.values, zs=df.CYCLE, zdir='x', alpha=0.8)

        ax.set_xlabel('CYCLE')
        ax.set_ylabel('NODE_ID')

        plt.show()

