import networkx as nx


def create_diamond(N, k, dashed):
    net = nx.DiGraph()
    s = 0
    for i in xrange(N):
        e = s + k + 1
        for n in range(k):
            node = s + n + 1
            net.add_edge(s, node, cap=1)
            net.add_edge(node, e, cap=1)
        if dashed:
            net.add_edge(e, e + 1, cap=k)
            s = e + 1
        else:
            s = e
    return net
