import line_patterns


def create(d):
    if 'topology' not in d:
        raise Exception('topology is missing in pattern.create')
    topology = d['topology']

    if topology == 'line':
        if 'type' not in d:
            raise Exception('type is missing in pattern.create')

        if 'N' not in d:
            raise Exception('N is missing in pattern.create')

        if d['type'] == 'uniform':
            return line_patterns.Uniform(d['N'])

        if d['type'] == 'uniform_init':
            return line_patterns.UniformWithInitializations(d['N'])

        if d['type'] == 'uniform_rate':
            if 'rate' not in d:
                raise Exception('rate is missing in pattern.create')
            return line_patterns.UniformRate(d['N'], d['rate'])

        if d['type'] == 'burst':
            if 'p_n2b' not in d or 'p_b2n' not in d:
                raise Exception('p_n2b or p_b2n are missing in pattern.create')
            if 'rate' in d: rate = d['rate']
            else: rate = 1
            return line_patterns.BurstyRate(d['N'], rate, d['p_n2b'], d['p_b2n'])

        if d['type'] == 'split':
            if 'num_splits' not in d:
                raise Exception('num_splits is missing in pattern.create')
            if 'rate' in d: rate = d['rate']
            else: rate = 1
            return line_patterns.MultiSplitPathRate(d['N'], d['num_splits'], rate)

    raise Exception('Unknwon pattern for {}'.format(d))