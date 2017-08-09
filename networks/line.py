import networkx as nx


def create_line(C, N):
    net = nx.DiGraph()
    for i in xrange(N):
        net.add_edge(i, i + 1, cap=C)
    return net
