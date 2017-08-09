from units import runner, results_to_file
import numpy as np

writer = results_to_file.ResultHandler('line2')
N = 200
cycles = 100000
num_runs = 1
for run_id in range(num_runs):
    protocols = [
        {'type': 'greedy', 'scheduler': 'LIS'},
        {'type': 'simple_downhill', 'dh_type': 'downhill', 'scheduler': 'LIS'},
        {'type': 'simple_downhill', 'dh_type': 'weak_downhill', 'scheduler': 'LIS'},
        {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
    ]
    for p in np.arange(0, 1.1, .1):
        protocols.append({'type': 'simple_downhill', 'dh_type': 'dgh', 'scheduler': 'LIS', 'p': p})
        protocols.append({'type': 'simple_downhill', 'dh_type': 'wgh', 'scheduler': 'LIS', 'p': p})
        protocols.append({'type': 'simple_downhill', 'dh_type': 'wdh', 'scheduler': 'LIS', 'p': p})

    test = {
        'test': {'id': 2, 'desc':'Hybrid schemes, single destination line, C=1'},
        'net': {'topology':'line', 'capacity': 1, 'N': N},
        'pattern': {'topology':'line', 'type':'uniform', 'N':N},
        'cycles': cycles,
        'run_id': run_id,
        'protocols': protocols
    }

    out = runner.run_single_sim(test)
    writer.write(out)

writer.close()
