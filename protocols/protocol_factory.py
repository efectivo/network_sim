import greedy, down_hill
import forwarding_buffer

def create(d):
    if 'type' not in d:
        raise Exception('type is missing in protocol.create')
    if 'scheduler' not in d:
        raise Exception('scheduler is missing in protocol.create')

    def get_scheduler(t):
        if t == 'LIS': return forwarding_buffer.LongestInSystem
        elif t == 'SIS': return forwarding_buffer.ShortestInSystem
        raise Exception('Unknown scheduler: {}'.format(t))
    scheduling_policy = get_scheduler(d['scheduler'])

    if d['type'] == 'greedy':
        return greedy.GreedyProtocol(scheduling_policy=scheduling_policy)

    if d['type'] == 'simple_downhill':
        if 'dh_type' not in d:
            raise Exception('dh_type is missing in protocol.create')
        flavor = d['dh_type']

        if flavor == 'downhill':
            return down_hill.SimpleDownHill(down_hill.Types.Downhill, scheduling_policy=scheduling_policy)
        if flavor == 'weak_downhill':
            return down_hill.SimpleDownHill(down_hill.Types.WeakDownhill, scheduling_policy=scheduling_policy)
        if flavor == 'odd_even_downhill':
            return down_hill.SimpleDownHill(down_hill.Types.OddEvenDownhill, scheduling_policy=scheduling_policy)

        if 'p' not in d:
            raise Exception('p is missing in protocol.create')

        if flavor == 'dgh':
            return down_hill.SimpleDownHill(down_hill.Types.DGHybrid, p=d['p'], scheduling_policy=scheduling_policy)
        if flavor == 'wgh':
            return down_hill.SimpleDownHill(down_hill.Types.WGHybrid, p=d['p'], scheduling_policy=scheduling_policy)
        if flavor == 'wdh':
            return down_hill.SimpleDownHill(down_hill.Types.WDHybrid, p=d['p'], scheduling_policy=scheduling_policy)

        else: raise Exception('Unknown downhill type')

    raise Exception('Unknown params {}'.format(d))