import networkx as nx
import matplotlib.pyplot as plt
import random


def create_random_weighted_dag(n, max_cap=10):
    random_graph = nx.gnp_random_graph(n, 0.5, directed=True)
    dag = nx.DiGraph([(u, v, {'cap': random.randint(1, max_cap)}) for (u, v) in random_graph.edges() if u < v])
    return dag


def create_path_graph(n, cap=None):
    g = nx.path_graph(n)
    if not cap: # cap == 1 by default
        return g

    for _,vd in g.edge.iteritems():
        for _,d in vd.iteritems():
            d['cap'] = 2
    return g


def draw(g):
    pos = nx.spring_layout(g)
    nx.draw(g, pos)
    n = len(g.nodes())
    nx.draw_networkx_labels(g, pos, dict(zip(range(n), range(n))))
    labels = nx.get_edge_attributes(g, 'cap')
    #print labels
    nx.draw_networkx_edge_labels(g, pos, edge_labels=labels)
    plt.show()