from units import environment, tested_unit
import itertools
import logging
import json
import copy
from networks import network_factory
from patterns import pattern_factory
from protocols import protocol_factory

def run_single_sim(d):
    print 'Running: ', d

    if 'net' not in d:
        raise Exception('net not in test dictionary')
    net = network_factory.create(d['net'])
    if 'pattern' not in d:
        raise Exception('pattern not in test dictionary')
    pattern = pattern_factory.create(d['pattern'])
    if 'cycles' not in d:
        raise Exception('cycles not in test dictionary')
    setup = environment.EnvironmentSetup(net, pattern, d['cycles'], logging.ERROR)

    if 'protocols' not in d:
        raise Exception('protocol not in test dictionary')
    tests = []
    protocols = d['protocols']
    for protocol in protocols:
        dcopy = copy.copy(d)
        del dcopy['protocols']
        dcopy['protocol'] = protocol
        protocol = protocol_factory.create(protocol)
        test = tested_unit.Test(dcopy, protocol)
        tests.append(test)

    env = environment.Environment(setup, tests)
    env.run()

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


# def run_test(test_desc, setups_gen, protocols_gen, schedulers):
#     f = open(r'C:\Temp\bla.json', 'wt')
#     first = True
#     f.write('[\n')
#     for setup in setups_gen():
#         tests = []
#         for protocol in protocols_gen():
#             desc = {'test': test_desc, 'net': setup.network.get_desc(), 'pattern': setup.pattern.get_desc(),
#                     'cycles': setup.cycle_number, 'protocol': protocol.get_desc(), 'scheduler': protocol.scheduling_policy.name}
#
#             test = tested_unit.Test(desc, protocol)
#             tests.append(test)
#
#         env = environment.Environment(setup, tests)
#         env.run()
#
#
#         for test in tests:
#             if first: first = False
#             else: f.write(',\n')
#             json.dump(test.desc, f)
#         f.flush()
#     f.write(']\n')
#     f.close()
