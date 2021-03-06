from units import runner
import numpy as np


def job_gen():
    for N in range(4, 21, 2):
        for rate_power in [1, 3/2.]:
            rate = np.power(N, rate_power)
            test = {
                'test': {},
                'net': {'topology': 'grid', 'N': N},
                'pattern': {'type': 'random_one_bent', 'rate': rate, 'power': rate_power},
                'cycles': 100000,
                'protocols': [
                    {'type': 'greedy', 'scheduler': 'LIS'},
                    {'type': 'goed', 'dh_type':'ogh', 'p': .1, 'scheduler': 'LIS'},
                    {'type': 'goed', 'dh_type': 'ogh', 'p': .5, 'scheduler': 'LIS'}
                ]
            }
            yield test

runner.run_parallel(15, job_gen, 'grid1')
