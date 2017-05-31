import os, datetime

class ResultHandler(object):
    def __init__(self, setup_desc, output_dir=r'E:\TOAR2\Network\Latex\results'):
        self.output_dir = output_dir
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        output_file_name = os.path.join(self.output_dir, '{}_{}.csv'.format(setup_desc, now))
        assert not os.path.exists(output_file_name)
        self.output_file = open(output_file_name, 'wt')
        print 'Opening {} for writing'.format(output_file_name)
        self.output_file.write('net,pattern,cycle_number,forwarding_protocol,scheduling_policy,max_buffer_size,average_packet_delay,max_packet_delay,average_delay_factor,max_delay_factor\n')

    def __del__(self):
        self.output_file.close()

    def write(self, net, pattern, cycle_number, test):
        self.output_file.write('{},{},{},{},{},'.format(net, pattern, cycle_number, test.forwarding_protcol.name,
                                                       test.forwarding_protcol.buffer_type().name))
        rep = test.reporter
        self.output_file.write('{},{},{},{},{}\n'.format(rep.max_buffer_size, rep.average_packet_delay,
                                                rep.max_packet_delay, rep.average_delay_factor, rep.max_delay_factor))

        self.output_file.flush()

