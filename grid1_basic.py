from units import runner
import numpy as np


def job_gen():
    for N in range(4, 21, 2):
        for rate in [N, N*np.sqrt(N)]:
            for p in [.1, .5]:
                test = {
                    'test': {},
                    'net': {'topology': 'grid', 'N': N},
                    'pattern': {'type': 'random_one_bent', 'rate': rate},
                    'cycles': 100000,
                    'protocols': [
                        {'type': 'greedy', 'scheduler': 'LIS'},
                        {'type': 'goed', 'dh_type':'ogh', 'p':p, 'scheduler': 'LIS'}
                    ]
                }
                yield test

runner.run_parallel(15, job_gen, 'grid1')
