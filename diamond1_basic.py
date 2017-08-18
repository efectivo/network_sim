from units import runner, results_to_file

def job_gen():
    run_num = 1
    for dashed in [0, 1]:
        for N in range(10, 101, 10):
            k = 3
            for run_id in range(run_num):
                test = {
                    'test': {},
                    'net': {'topology': 'diamond', 'dashed': dashed, 'N': N, 'k': k},
                    'pattern': {'type': 'uniform_src_poisson_rate'},
                    'run_id': run_id,
                    'cycles': 100000,
                    'protocols': [
                        {'type': 'greedy', 'scheduler': 'LIS'},
                        {'type': 'goed', 'scheduler': 'LIS'}
                    ]
                }

                yield test

        for k in range(1, 11):
            N = 50
            for run_id in range(run_num):
                test = {
                    'test': {},
                    'net': {'topology': 'diamond', 'dashed': dashed, 'N': N, 'k': k},
                    'pattern': {'type': 'uniform_src_poisson_rate'},
                    'run_id': run_id,
                    'cycles': 100000,
                    'protocols': [
                        {'type': 'greedy', 'scheduler': 'LIS'},
                        {'type': 'goed', 'scheduler': 'LIS'}
                    ]
                }

                yield test


class Counter:
    QQ = 0

def job_run(test):
    Counter.QQ += 1
    print Counter.QQ, test
    out = runner.run_single_sim(test)
    print Counter.QQ, out
    return out

import multiprocessing
p = multiprocessing.Pool(15)
writer = results_to_file.ResultHandler('diamond1')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

