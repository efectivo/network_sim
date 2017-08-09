import line_patterns


def create(d):
    if 'topology' not in d:
        raise Exception('topology is missing in pattern.create')
    topology = d['topology']

    if topology == 'line':
        if 'type' not in d:
            raise Exception('type is missing in pattern.create')

        if d['type'] == 'uniform':
            if 'N' not in d:
                raise Exception('N is missing in pattern.create')
            return line_patterns.Uniform(d['N'])

        if d['type'] == 'uniform_init':
            if 'N' not in d:
                raise Exception('N is missing in pattern.create')
            return line_patterns.UniformWithInitializations(d['N'])

    raise Exception('Unknwon pattern for {}'.format(d))