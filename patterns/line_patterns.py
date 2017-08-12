import patterns
import random
from units import packet


class Uniform(patterns.PatternIfc):
    def __init__(self, N):
        self.N = N # Src is random 0 - N-1, dst is N

    def invoke(self, curr_cycle):
        src = random.randint(0, self.N-1)
        return [packet.Packet(range(src, self.N+1), curr_cycle)]


class UniformWithInitializations(patterns.PatternIfc):
    def __init__(self, N):
        self.N = N # Src is random 0 - N-1, dst is N

    def invoke(self, curr_cycle):
        if curr_cycle == 0:
            return [packet.Packet(range(src, self.N+1), curr_cycle) for src in range(self.N)]

        src = random.randint(0, self.N-1)
        return [packet.Packet(range(src, self.N+1), curr_cycle)]


class UniformRate(patterns.PatternIfc):
    def __init__(self, N, p_inj = 1):
        self.N = N # Src is random 0 - N-1, dst is N
        self.p_inj = p_inj # Injection probability

    def invoke(self, curr_cycle):
        if random.random() > self.p_inj: # Don't inject
            return []

        src = random.randint(0, self.N-1)
        return [packet.Packet(range(src, self.N+1), curr_cycle)]


class BurstyRate(UniformRate):
    STATE_NORMAL = 0
    STATE_BURST = 1

    def __init__(self, N, p_inj = 1, p_normal_to_burst = 0, p_burst_to_normal = 1):
        UniformRate.__init__(self, N, p_inj)
        self.p_normal_to_burst = p_normal_to_burst
        self.p_burst_to_normal = p_burst_to_normal
        self.state = self.STATE_NORMAL
        self.prev_src = random.randint(0, self.N-1)

    def invoke(self, curr_cycle):
        if self.state == self.STATE_BURST:
            # BURST STATE:

            if random.random() < self.p_burst_to_normal:
                self.state = self.STATE_NORMAL

            # Sends a packet from the previous source with prob 1
            return [packet.Packet(range(self.prev_src, self.N + 1), curr_cycle)]

        # NORMAL STATE
        if random.random() < self.p_normal_to_burst:
            self.state = self.STATE_BURST

        p = UniformRate.invoke(self, curr_cycle)

        if not p:
            return []

        self.prev_src = p[0].route[0]
        return p

