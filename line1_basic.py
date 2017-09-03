from units import runner

def job_gen():
    for N in range(50, 501, 50):
        for run_id in range(10):
            test = {
                'test': {'id': 1, 'desc':'Buffer size vs Network size on the line'},
                'net': {'topology':'line', 'capacity':1, 'N':N},
                'pattern': {'type':'uniform'},
                'cycles': N**2,
                'run_id': run_id,
                'protocols': [
                    {'type': 'greedy', 'scheduler':'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'downhill', 'scheduler': 'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'weak_downhill', 'scheduler': 'LIS'},
                    {'type': 'simple_downhill', 'dh_type': 'odd_even_downhill', 'scheduler': 'LIS'}
                ]
            }
            yield test

runner.run_parallel(15, job_gen, 'line_basic_test')
