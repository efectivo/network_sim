import Queue
import heapq
import random


class BufferIfc(object):
    def __init__(self):
        self.values = None

    def insert(self, packet):
        pass

    def extract(self):
        return None

    def __len__(self):
        return 0


class Fifo(BufferIfc):
    def __init__(self):
        self.queue = Queue.Queue()
        self.values = self.queue

    def insert(self, packet):
        self.queue.put(packet)

    def extract(self):
        return self.queue.get()

    def __len__(self):
        return self.queue.qsize()


class Lifo(BufferIfc):
    def __init__(self):
        self.stack = []
        self.values = self.stack

    def insert(self, packet):
        self.stack.append(packet)

    def extract(self):
        return self.stack.pop()

    def __len__(self):
        return len(self.stack)


class LongestInSystem(BufferIfc):
    def __init__(self):
        self.heap = []
        self.values = self.heap

    def insert(self, packet):
        heapq.heappush(self.heap, (packet.invoke_cycle, packet))

    def extract(self):
        invoke_cycle, packet = heapq.heappop(self.heap)
        return packet

    def __len__(self):
        return len(self.heap)

    def top(self):
        return self.heap[0]


class ShortestInSystem(LongestInSystem):
    def __init__(self):
        LongestInSystem.__init__(self)

    def insert(self, packet):
        heapq.heappush(self.heap, (-packet.invoke_cycle, packet))


class ClosestToSrc(LongestInSystem):
    def __init__(self):
        LongestInSystem.__init__(self)

    def insert(self, packet):
        heapq.heappush(self.heap, (packet.curr_hop, packet))

class FurthestFromSrc(LongestInSystem):
    def __init__(self):
        LongestInSystem.__init__(self)

    def insert(self, packet):
        heapq.heappush(self.heap, (-packet.curr_hop, packet))


class ShortestToGo(LongestInSystem):
    def __init__(self):
        LongestInSystem.__init__(self)

    def insert(self, packet):
        heapq.heappush(self.heap, (len(packet.route) - packet.curr_hop, packet))


class FurthestToGo(LongestInSystem):
    def __init__(self):
        LongestInSystem.__init__(self)

    def insert(self, packet):
        heapq.heappush(self.heap, (packet.curr_hop-len(packet.route), packet))


class Rand(BufferIfc):
    def __init__(self):
        self.values = []
        self.count = 0

    def insert(self, packet):
        self.count += 1
        self.values.append(packet)

    def extract(self):
        self.count -= 1
        i = random.randint(0, self.count) # inclusive
        return self.values.pop(i)

    def __len__(self):
        return self.count

