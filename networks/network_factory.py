import line, diamond, grid

def create(d):
    if 'topology' not in d:
        raise Exception('topology is missing in network.create')

    topology = d['topology']
    if topology == 'line':
        if 'capacity' not in d or 'N' not in d:
            raise Exception('capacity or N are missing in network.create')
        return line.create_line(C=d['capacity'], N=d['N'])
    elif topology == 'diamond':
        dashed = 'dashed' in d and d['dashed']
        if 'N' not in d or 'k' not in d:
            raise Exception('N or k are missing in network.create')
        return diamond.create_diamond(d['N'], d['k'], dashed)
    elif topology == 'grid':
        if 'N' not in d:
            raise Exception('N is missing in network.create')
        return grid.create_grid(d['N'])

    raise Exception('Unknown params {}'.format(d))