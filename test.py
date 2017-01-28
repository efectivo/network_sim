import simulation, network_factory, policy, algo, units, buffer, logging, random
import datetime
import networkx as nx

# for cycle in [10, 100, 1000, 10000]:
#     for graph in [10, 100, 1000, 10000]:
#         start = datetime.datetime.now()
#
#         net = network_factory.create_path_graph(graph)
#         policies = [policy.RandomSrcSameDest(net)]
#         alg = algo.Greedy
#         s = simulation.Sim(alg, net, policies, buffer.LongestInSystem, cycle, logging.INFO, False)
#         s.run()
#         #s.reporter.print_stats()
#         #s.reporter.df
#         #print s.reporter.packet_delay
#         #s.reporter.plot_graphs()
#         #s.reporter.plot_buffer_state()
#
#         end = datetime.datetime.now()
#         print cycle, graph, end - start
# #network_factory.draw(networkx.degree_sequence_tree(networkx.random_powerlaw_tree_sequence(20,3.5,1, 10000)))

# net = network_factory.create_path_graph(10)
# policies = [policy.RandomSrcSameDest(net, range(4), 9)]
# alg = algo.Greedy()
# s = simulation.Sim(alg, net, policies, buffer.LongestInSystem, 30, logging.INFO, True)
# s.run()
# s.reporter.plot_buffer_state()

net = network_factory.create_tree_from_split_list([1,3,1,2,2])
leaves = [x for x in net.nodes_iter() if not net.in_degree(x)]
#policies = [policy.RandomSrcSameDest(net, leaves, 0)]
policies = []
for leaf in leaves:
    p_off = random.random()
    p_on = p_off / (len(leaves)-1)
    policies.append(policy.OnOff(net, leaf, 0, p_on, p_off))
#alg = algo.DownHill(True)
alg = algo.Greedy()
s = simulation.Sim(alg, net, policies, buffer.LongestInSystem, 100, logging.DEBUG, True)
s.run()
s.reporter.print_stats()
