from units import runner, results_to_file
import multiprocessing
import itertools
import copy


def job_gen():
    num_runs = 1
    N = 300
    for k in range(1, 6):
        for C in range(1, 11):
            test = {
                'test': {'id': 6, 'desc': 'Effect of multiple destinations'},
                'net': {'topology': 'line', 'capacity': C, 'N': N},
                'cycles': N ** 2,
                'protocols': [
                    {'type': 'greedy', 'scheduler': 'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
                ],
                'pattern': {'composite': C, 'topology': 'line', 'type': 'split', 'N': N, 'num_splits': k}
            }
            yield test



def job_run(test):
    print test['pattern']
    return runner.run_single_sim(test)

p = multiprocessing.Pool(15)
writer = results_to_file.ResultHandler('line6')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

