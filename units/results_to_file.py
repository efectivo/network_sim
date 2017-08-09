import os, datetime, json

class ResultHandler(object):
    def __init__(self, name, output_dir=r'E:\TOAR2\Network\Latex\json'):
        self.output_dir = output_dir
        now = datetime.datetime.now().strftime('%Y%m%d_%H%M')
        output_file_name = os.path.join(self.output_dir, '{}_{}.json'.format(name, now))
        assert not os.path.exists(output_file_name)
        self.f = open(output_file_name, 'wt')
        print 'Opening {} for writing'.format(output_file_name)
        self.first = True
        self.f.write('[\n')

    def close(self):
        self.f.write(']\n')
        self.f.close()

    def write(self, d):
        if self.first:
            self.first = False
        else:
            self.f.write(',\n')
        json.dump(d, self.f)
        self.f.flush()

