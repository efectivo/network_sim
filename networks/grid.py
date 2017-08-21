import networkx as nx


def get_node(N, row, col):
    return row * N + col


def create_grid(N):

    net = nx.DiGraph()
    for i in xrange(N):
        for j in xrange(N-1):
            net.add_edge(get_node(N, i, j), get_node(N, i, j + 1))
            net.add_edge(get_node(N, i, j + 1), get_node(N, i, j))
            net.add_edge(get_node(N, j, i), get_node(N, j + 1, i))
            net.add_edge(get_node(N, j + 1, i), get_node(N, j, i))
    return net
