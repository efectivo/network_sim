from units import runner, results_to_file

writer = results_to_file.ResultHandler('line3')
for N in range(50, 501, 50):
    for run_id in range(3):
        for pattern_type in ['uniform', 'uniform_init']:
            test = {
                'test': {'id': 3, 'desc': 'Effect of load initialization on max load'},
                'net': {'topology':'line', 'capacity':1, 'N':N},
                'pattern': {'topology':'line', 'type':pattern_type, 'N':N},
                'cycles': N**2,
                'run_id': run_id,
                'protocols': [
                    {'type': 'greedy', 'scheduler':'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
                ]
            }

            out = runner.run_single_sim(test)
            writer.write(out)

writer.close()
