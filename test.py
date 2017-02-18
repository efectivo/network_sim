import simulation, network_factory, policy, algo, units, buffer, logging, random, reporter

net = network_factory.create_random_weighted_dag(10)

# Configuration for trees
net = network_factory.create_tree_from_split_list([1,3,1,2,2])
leaves = [x for x in net.nodes_iter() if not net.in_degree(x)]
policies = []
for leaf in leaves:
    p_off = random.random()
    p_on = p_off / (len(leaves)-1)
    policies.append(policy.OnOff(net, leaf, 0, p_on, p_off))
test1 = simulation.Test('greedy', algo.Greedy(), buffer.LongestInSystem)
test2 = simulation.Test('odd_even', algo.DownHill(use_odd_even=True), buffer.LongestInSystem)
test3 = simulation.Test('down_hill', algo.DownHill(use_odd_even=False), buffer.LongestInSystem)
tests = [test1, test2, test3]
sim_config = simulation.SimulationConfig(net, policies, 100, logging.DEBUG)
s = simulation.Sim(sim_config, tests)
s.run()
