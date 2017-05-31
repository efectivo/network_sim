import collections

class BufferComposite(object):
    def __init__(self, buffer_type):
        self.buffers = collections.defaultdict(buffer_type)
        self.name = buffer_type().name

    def insert(self, packet):
        two_hops_node = packet.get_two_hops()
        buf = self.buffers[two_hops_node]
        buf.insert(packet)

    def extract(self, **kvdict):
        two_hops_node = kvdict.get('two_steps_node')
        assert two_hops_node in self.buffers
        buf = self.buffers[two_hops_node]
        return buf.extract()

    def __len__(self):
        return sum([len(buf) for buf in self.buffers.values()])

    def get_buf_len(self, buf_name):
        return len(self.buffers[buf_name])

    def get_top_packet_id(self, buf_name):
        buf = self.buffers[buf_name]
        if not buf:
            return None
        return self.buffers[buf_name].top()[1].packet_id


