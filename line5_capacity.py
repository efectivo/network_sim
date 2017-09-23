from units import runner, results_to_file
import multiprocessing
import itertools
import copy


def job_gen():
    run_id = 1
    N = 300
    for C in range(1, 11):

        base_test = {
            'test': {'id': 5, 'desc': 'Effect of capacity'},
            'net': {'topology': 'line', 'capacity': C, 'N': N},
            'cycles': N ** 2,
            'protocols': [
                {'type': 'greedy', 'scheduler': 'LIS'},
                {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
            ]
        }

        test = copy.copy(base_test)
        test['pattern'] = {'composite': C, 'topology': 'line', 'type': 'uniform', 'N': N}
        test['run_id'] = run_id
        yield test

        probs = [.9, .5, .1]
        for p_n2b, p_b2n in itertools.product(probs, probs):
            test = copy.copy(base_test)
            test['pattern'] = {'composite': C, 'topology':'line', 'type':'burst', 'p_n2b':p_n2b, 'p_b2n':p_b2n, 'N':N}
            test['run_id'] = run_id
            yield test


def job_run(test):
    print test['pattern']
    return runner.run_single_sim(test)

p = multiprocessing.Pool(15)
writer = results_to_file.ResultHandler('line5')
all_results = p.map(job_run, job_gen())
for result in all_results:
    writer.write(result)
writer.close()

