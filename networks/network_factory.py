import line

def create(d):
    if 'topology' not in d:
        raise Exception('topology is missing in network.create')

    topology = d['topology']
    if topology == 'line':
        if 'capacity' not in d or 'N' not in d:
            raise Exception('capacity or N are missing in network.create')
        return line.create_line(C=d['capacity'], N=d['N'])

    raise Exception('Unknown params {}'.format(d))