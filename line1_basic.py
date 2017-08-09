from units import runner, results_to_file

writer = results_to_file.ResultHandler('line1')
for N in range(50, 501, 50):
    for run_id in range(10):
        test = {
            'test': {'id': 1, 'desc':'Buffer size vs Network size on the line'},
            'net': {'topology':'line', 'capacity':1, 'N':N},
            'pattern': {'topology':'line', 'type':'uniform', 'N':N},
            'cycles': N**2,
            'run_id': run_id,
            'protocols': [
                {'type': 'greedy', 'scheduler':'LIS'},
                {'type': 'simple_downhill', 'dh_type': 'downhill', 'scheduler': 'LIS'},
                {'type': 'simple_downhill', 'dh_type': 'weak_downhill', 'scheduler': 'LIS'},
                {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
            ]
        }

        out = runner.run_single_sim(test)
        writer.write(out)

writer.close()

#
# def setup_gen(): # Return network with N+1 nodes
#     #for N in range(50, 501, 50):
#     for N in [50,]:
#         setup = environment.EnvironmentSetup(net, line_patterns.Uniform(N), N**2, logging.INFO)
#         yield setup
#
# def protocol_gen():
#     yield greedy.GreedyProtocol()
#     yield down_hill.SimpleDownHill(down_hill.Types.Downhill)
#     yield down_hill.SimpleDownHill(down_hill.Types.WeakDownhill)
#     yield down_hill.SimpleDownHill(down_hill.Types.OddEvenDownhill)
#
# # TODO add sch policy
# runner.run_test(test_desc, setup_gen,
#                 protocol_gen,
#                 [forwarding_buffer.LongestInSystem])
