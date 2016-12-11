import units

class Policy(object):
    def __init__(self):
        pass

    def invoke(self):
        pass


class SendEachCycleTo(Policy):
    def __init__(self, dst, count=1):
        Policy.__init__(self)
        self.dst = dst
        self.count = count

    def invoke(self):
        return [units.Packet(self.dst) for _ in xrange(self.count)]
