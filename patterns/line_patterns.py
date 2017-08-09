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

