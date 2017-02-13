import simulation, network_factory, policy, algo, units, buffer, logging, random

net = network_factory.create_tree_from_split_list([1,3,1,2,2])
leaves = [x for x in net.nodes_iter() if not net.in_degree(x)]
policies = []
for leaf in leaves:
    p_off = random.random()
    p_on = p_off / (len(leaves)-1)
    policies.append(policy.OnOff(net, leaf, 0, p_on, p_off))
alg = algo.Greedy()
#alg = algo.DownHill(use_odd_even=False)
s = simulation.Sim(alg, net, policies, buffer.LongestInSystem, 100, logging.DEBUG, False, True)
s.run()
s.reporter.print_stats()
