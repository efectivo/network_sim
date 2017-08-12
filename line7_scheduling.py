from units import runner, results_to_file
import multiprocessing
import itertools
import copy


def job_gen():
    num_runs = 5
    N = 200
    for k in range(1, 6):
        for run_id in range(num_runs):
            for rate in [1.1, 1, 0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5]:
                for sp in ['LIS', 'SIS', 'LIFO', 'FIFO', 'FTG', 'STG', 'CTS', 'FFS', 'RAND']:
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



def job_run(test):
    print test['pattern']
    return runner.run_single_sim(test)

p = multiprocessing.Pool(5)
writer = results_to_file.ResultHandler('line7')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

