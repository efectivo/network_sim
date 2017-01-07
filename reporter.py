import matplotlib.pyplot as plt
import pandas as pd

from mpl_toolkits.mplot3d import Axes3D
import numpy as np


class Reporter(object):
    """
    This class collect the statistics and aggregate them.
    Print simulation summary at the end.
    """
    def __init__(self, services, cycle_num):
        self.services = services
        self.total_packets_sent = 0
        self.total_packets_recv = 0
        self.total_cycles = 0
        self.stats = {}
        self.df = None

    def packets_invoked(self, packets):
        self.total_packets_sent += len(packets)

    def packet_received(self, packet):
        self.total_packets_recv += 1
        self.total_cycles += self.services.curr_cycle - packet.invoke_cycle

    def update_buffer_size(self, name, curr_max_buffer_size, curr_mean_buffer_size):
        self.stats[(name, self.services.curr_cycle)] = (curr_max_buffer_size, curr_mean_buffer_size)

    def finalize(self):
        df = pd.DataFrame(self.stats).T
        df.columns = ['BUF', 'MEAN_BUF'] # Relevant only when there is more than one port
        df.index.names = ['NODE', 'CYCLE']
        self.df = df.reset_index()

    def print_stats(self):
        print 'Total sent: {}'.format(self.total_packets_sent)
        print 'Total recv: {}'.format(self.total_packets_recv)
        print 'Avg cycles: {}'.format(self.total_cycles / self.total_packets_recv)

    def plot_graphs(self):
        df = self.df.groupby('CYCLE').BUF
        df.agg(['max', 'mean']).plot(title='Buffer statistics per node')
        plt.show()

    def plot_buffer_state(self):
        fig = plt.figure()
        ax = fig.add_subplot(111, projection='3d')
        df = self.df
        ax.bar(df.NODE, df.BUF.values, zs=df.CYCLE, zdir='x', alpha=0.8)

        ax.set_xlabel('CYCLE')
        ax.set_ylabel('NODE_ID')

        plt.show()
