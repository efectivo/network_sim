from units import runner, results_to_file
import multiprocessing
import itertools
import copy


def job_gen():
    num_runs = 5
    for N in [100, 200, 300, 400, 500]:
        for run_id in range(num_runs):
            for k in range(1, 6):
                for C in range(1, 11):
                    test = {
                        'test': {'id': 6, 'desc': 'Effect of multiple destinations'},
                        'net': {'topology': 'line', 'capacity': 1, 'N': N},
                        'cycles': N ** 2,
                        'protocols': [
                            {'type': 'greedy', 'scheduler': 'LIS'},
                            {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
                        ],
                        'run_id': run_id,
                        'pattern': {'composite': C, 'topology': 'line', 'type': 'split', 'N': N, 'num_splits': k}
                    }
                    yield test



def job_run(test):
    print test['pattern']
    return runner.run_single_sim(test)

p = multiprocessing.Pool(8)
writer = results_to_file.ResultHandler('line6')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

