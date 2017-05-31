class Packet(object):
    next_packet_id = 0

    def __init__(self, pattern_name, route, curr_cycle):
        self.pattern_name = pattern_name
        self.route = route
        self.invoke_cycle = curr_cycle
        self.curr_hop = 0
        self.packet_id = Packet.next_packet_id
        Packet.next_packet_id += 1

    def get_next_hop(self):
        if self.curr_hop == len(self.route):
            return None
        return self.route[self.curr_hop]

    def get_two_hops(self):
        assert self.curr_hop != len(self.route)

        if self.curr_hop + 1 == len(self.route):
            return None

        return self.route[self.curr_hop + 1]

    def packet_received(self):
        self.curr_hop += 1

    def __repr__(self):
        return 'PID:{}/{}. {}->{}'.format(self.packet_id, self.invoke_cycle, self.route[0], self.route[-1])

