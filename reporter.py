import matplotlib.pyplot as plt
import pandas as pd
import collections
import logging
import networkx as nx


class Reporter(object):
    """
    This class collect the statistics and aggregate them.
    Print simulation summary at the end.
    """
    def __init__(self, services, calc_history=False):
        self.services = services
        self.total_packets_sent = 0
        self.total_packets_recv = 0
        self.invoke_logger = logging.getLogger('invoke')
        self.receive_logger = logging.getLogger('receive')

        # For animation
        self.fig = None
        self.new_packets = collections.defaultdict(int)

        self.calc_history = calc_history
        if calc_history:
            self.packet_delay = collections.OrderedDict()
            self.stats = {}
            self.df = None
            self.packet_delay_df = None
            self.packet_received = self.packet_received_history
            self.update_buffer_size = self.update_buffer_size_history
        else:
            self.total_delay = 0
            self.curr_max_buffer_size = 0
            self.curr_max_packet_delay = 0
            self.packet_received = self.packet_received_fast
            self.update_buffer_size = self.update_buffer_size_fast

    def packets_invoked(self, packets):
        self.total_packets_sent += len(packets)
        if self.services.verbose:
            for packet in packets:
                self.new_packets[packet.route[0]] += 1
                self.invoke_logger.debug(packet)

    def packet_received_fast(self, packet):
        self.total_packets_recv += 1
        max_packet_delay = self.services.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        self.curr_max_packet_delay = max(max_packet_delay, self.curr_max_packet_delay)
        self.total_delay += max_packet_delay
        self.receive_logger.debug(packet)

    def packet_received_history(self, packet):
        self.total_packets_recv += 1
        self.packet_delay[str(packet)] = self.services.curr_cycle - packet.invoke_cycle - (len(packet.route)-1)
        #if self.services.verbose:
        self.receive_logger.debug(packet)

    def update_buffer_size_fast(self, name, curr_max_buffer_size):
        self.curr_max_buffer_size = max(self.curr_max_buffer_size, curr_max_buffer_size)

    def update_buffer_size_history(self, name, curr_max_buffer_size):
        self.stats[(name, self.services.curr_cycle)] = (curr_max_buffer_size,)

    def finalize(self):
        if self.calc_history:
            df = pd.DataFrame(self.stats).T
            df.columns = ['BUF'] # Relevant only when there is more than one port
            df.index.names = ['NODE', 'CYCLE']
            self.df = df.reset_index()
            self.packet_delay_df = pd.Series(self.packet_delay.values())

    def print_stats(self):
        self.services.logger.info('Total sent: {}'.format(self.total_packets_sent))
        self.services.logger.info('Total recv: {}'.format(self.total_packets_recv))

        if not self.calc_history:
            self.services.logger.info('Max packet delay: {}'.format(self.curr_max_packet_delay))
            if self.total_packets_recv > 0:
                self.services.logger.info('Average packet delay: {}'.format(1.0*self.total_delay/self.total_packets_recv))
            self.services.logger.info('Max buffer size: {}'.format(self.curr_max_buffer_size))

    def plot_graphs(self):
        if not self.calc_history:
            return

        df = self.df.groupby('CYCLE').BUF
        df.agg(['max', 'mean']).plot(title='Buffer statistics per node')
        plt.show()

    def plot_buffer_state(self):
        from mpl_toolkits.mplot3d import Axes3D
        if not self.calc_history:
            return

        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        df = self.df
        ax.bar(df.NODE, df.BUF.values, zs=df.CYCLE, zdir='x', alpha=0.8)

        ax.set_xlabel('CYCLE')
        ax.set_ylabel('NODE_ID')

        plt.show()

    def animate(self):
        if not self.fig:
            self.fig = plt.figure()
            self.pos = nx.spring_layout(self.services.net)
            # pos = nx.spectral_layout(g)

        self.fig.clear()
        labels = {}
        node_color = []
        for node_name, node in self.services.nodes.iteritems():
            labels[node_name] = '({}):{}'.format(node_name, node.curr_total_packets)
            node_color.append('r' if self.new_packets[node_name] else 'g')

        nx.draw_networkx(self.services.net, self.pos, labels=labels,
                         node_size=1600, node_color=node_color,
                         node_shape='s', font_size=15)

        self.fig.show()
        self.fig.suptitle(self.services.curr_cycle, fontsize=20)
        plt.pause(5)
        self.new_packets = collections.defaultdict(int)
