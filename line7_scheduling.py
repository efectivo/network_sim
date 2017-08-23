from units import runner, results_to_file
import multiprocessing
import itertools
import copy


def job_gen():
    num_runs = 5
    N = 200
    for sp in ['LIS', 'SIS', 'LIFO', 'FIFO', 'FTG', 'STG', 'CTS', 'FFS', 'RAND']:
        for run_id in range(num_runs):
            for rate in [1, 0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5]:
                test = {
                    'test': {'id': 7, 'desc': 'Effect of scheduling policy'},
                    'net': {'topology': 'line', 'capacity': 1, 'N': N},
                    'cycles': 50000,
                    'protocols': [
                        {'type': 'greedy', 'scheduler': sp},
                        {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': sp}
                    ],
                    'run_id': run_id,
                    'pattern': {'topology': 'line', 'type': 'uniform_rate', 'N': N, 'rate': rate}
                }
                yield test

                for k in range(1, 6):
                        test = {
                            'test': {'id': 7, 'desc': 'Effect of scheduling policy'},
                            'net': {'topology': 'line', 'capacity': 1, 'N': N},
                            'cycles': 50000,
                            'protocols': [
                                {'type': 'greedy', 'scheduler': sp},
                                {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': sp}
                            ],
                            'run_id': run_id,
                            'pattern': {'topology': 'line', 'type': 'split', 'N': N, 'num_splits': k, 'rate': rate}
                        }
                        yield test

runner.run_parallel(15, job_gen, 'line7')
