from units import runner, results_to_file
import multiprocessing
import itertools


def job_gen():
    N = 200
    cycles = 50000
    run_id = 1
    for rate in [1.1, 1, 0.99, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5]:
        test = {
            'test': {'id': 4, 'desc': 'Effect of Decreased Rate'},
            'net': {'topology': 'line', 'capacity': 1, 'N': N},
            'pattern': {'topology': 'line', 'type': 'uniform_rate', 'rate':rate, 'N': N},
            'cycles': cycles,
            'run_id': run_id,
            'protocols': [
                {'type': 'greedy', 'scheduler': 'LIS'},
                {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
            ]
        }
        yield test

        probs = map(lambda x: 1./x, [2,5,10,25,50,75,100])
        for p_n2b, p_b2n in itertools.product(probs, probs):
            test = {
                'test': {'id': 4, 'desc': 'Effect of Burstiness vs rate'},
                'net': {'topology': 'line', 'capacity': 1, 'N': N},
                'pattern': {'topology':'line', 'type':'burst', 'rate':rate, 'p_n2b':p_n2b, 'p_b2n':p_b2n, 'N':N},
                'cycles': cycles,
                'run_id': run_id,
                'protocols': [
                    {'type': 'greedy', 'scheduler':'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
                ]
            }
            yield test

def job_run(test):
    return runner.run_single_sim(test)

p = multiprocessing.Pool(8)
writer = results_to_file.ResultHandler('line4')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

