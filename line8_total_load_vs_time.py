from units import runner, results_to_file
import multiprocessing
import itertools
import copy


N = 100
cycles = 1000000
test = {
    'test': {'id': 8, 'desc': 'Load vs time'},
    'net': {'topology': 'line', 'capacity': 1, 'N': N},
    'cycles': cycles,
    'protocols': [
        {'type': 'greedy', 'scheduler': 'LIS', 'total_count_path':r'c:\Temp\total_count.hdf'},
    ],
    'pattern': {'topology': 'line', 'type': 'uniform', 'N': N}
}

runner.run_single_sim(test)

