from units import environment, tested_unit, test_reporter
import multiprocessing
import logging
import copy
import results_to_file
from networks import network_factory
from patterns import pattern_factory
from protocols import protocol_factory

def run_single_sim(d):
    if 'net' not in d:
        raise Exception('net not in test dictionary')
    net = network_factory.create(d['net'])
    if 'pattern' not in d:
        raise Exception('pattern not in test dictionary')
    d['pattern'].update(d['net'])
    pattern = pattern_factory.create(d['pattern'])
    if 'cycles' not in d:
        raise Exception('cycles not in test dictionary')
    setup = environment.EnvironmentSetup(net, pattern, d['cycles'], logging.ERROR)

    if 'protocols' not in d:
        raise Exception('protocol not in test dictionary')
    tests = []
    protocols = d['protocols']
    for protocol_dict in protocols:
        dcopy = copy.copy(d)
        del dcopy['protocols']
        dcopy['protocol'] = protocol_dict
        protocol = protocol_factory.create(protocol_dict)

        reporter = None
        if 'log_path' in protocol_dict:
            reporter = test_reporter.TestResultsLog(protocol_dict['log_path'])
        elif 'total_count_path' in protocol_dict:
            reporter = test_reporter.CountTotalLoadPerCycle(protocol_dict['total_count_path'])
        elif 'create_df' in protocol_dict:
            reporter = test_reporter.TestResultsHistory(protocol_dict['create_df'])

        test = tested_unit.Test(dcopy, protocol, reporter=reporter)
        tests.append(test)

    env = environment.Environment(setup, tests)
    env.run()

    # TODO
    if type(test.reporter) == test_reporter.CountTotalLoadPerCycle:
        return

    d['result'] = []
    for test in tests:
        res = {}
        res['max_load'] = test.reporter.max_buffer_size
        res['mean_max_load'] = test.reporter.average_max_buffer_size
        res['max_delay'] = test.reporter.max_packet_delay
        res['mean_delay'] = test.reporter.average_packet_delay
        res['mean_delay_f'] = test.reporter.average_delay_factor
        res['max_delay_f'] = test.reporter.max_delay_factor
        res['packets_recv_num'] = test.reporter.total_packets_recv
        d['result'].append(res)

    d['total_seconds'] = test.reporter.test_time.total_seconds()
    return d


def run_parallel(cores, job_generator, name):
    import multiprocessing
    p = multiprocessing.Pool(cores)
    writer = results_to_file.ResultHandler(name)
    all_results = p.map(run_single_sim, job_generator())
    for result in all_results:
        writer.write(result)
    writer.close()

