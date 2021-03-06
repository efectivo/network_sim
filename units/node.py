import collections
import logging

# A node in the graph, knows only it's neighbors' names.
# It asks for services from the outside world through the services member.
class Node(object):
    def __init__(self, name, network):
        self.name = name
        self.curr_total_packets = 0

        self.parents = network.predecessors(self.name)
        self.children = network.successors(self.name)

    def update_total_packets(self, diff):
        self.curr_total_packets += diff
