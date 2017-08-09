import forwarding_protocol
import forwarding_buffer
import forwarding_buffer_composite
import functools
import collections
import copy
import random

class TwoStepsDownHill(forwarding_protocol.ForwardingProtocol):
    def __init__(self, bypass_prob=0, use_two_stages=True, choose_max_randomaly=True, divide_by_fanout=False):
        buffer_creator_func = functools.partial(forwarding_buffer_composite.BufferComposite, forwarding_buffer.LongestInSystem)
        forwarding_protocol.ForwardingProtocol.__init__(self, buffer_type=buffer_creator_func)

        self.bypass_prob = bypass_prob
        if bypass_prob > 0:
            self.check_odd_even_rule = self.check_odd_even_rule_greedy_fallback
        else:
            self.check_odd_even_rule = self.check_odd_even_rule_orig
        self.use_two_stages = use_two_stages

        if choose_max_randomaly:
            self._calc_max_buffer = self._calc_max_buffer_randomaly
        else:
            self._calc_max_buffer = self._calc_max_buffer_lis

        self.divide_by_fanout = divide_by_fanout


    def init(self):
        self.node_capacity = {}
        for node in self.nodes.itervalues():
            self.node_capacity[node] = {}
            for parent in node.parents:
                self.node_capacity[node][parent] = node.edge_capacity_per_parent[parent.name]

    def run_communication_step(self):
        self.to_send = collections.defaultdict(int)
        for node in self.nodes.itervalues():
            self.run_communication_step_per_node(node)

    def run_communication_step_per_node(self, node):
        LAST_STOP_BUFFER = None

        # Set the a vailable capacity for parent-node edge
        curr_capacity = copy.copy(self.node_capacity[node])

        # Create a copy of the input and output state
        output_buffer_size = {}
        two_step_buffer_size = collections.defaultdict(dict)

        if self.use_two_stages:
            # First forward packets that this node is their destination, and update the capacity
            for parent in node.parents:
                buf = parent.buffers[node.name]
                last_buf_size = buf.get_buf_len(LAST_STOP_BUFFER)
                send_count = min(last_buf_size, curr_capacity[parent])
                self.to_send[parent, node, LAST_STOP_BUFFER] += send_count
                curr_capacity[parent] -= send_count

            for child in node.children:
                output_buffer_size[child] = len(node.buffers[child.name])
                for parent in node.parents:
                    buf_size = parent.buffers[node.name].get_buf_len(child.name)
                    if buf_size > 0:
                        two_step_buffer_size[child][parent] = buf_size

        else:
            output_buffer_size[LAST_STOP_BUFFER] = 0
            for child in node.children + [LAST_STOP_BUFFER]:
                if child is None:
                    name = None
                else:
                    name = child.name
                    output_buffer_size[child] = len(node.buffers[name])

                for parent in node.parents:
                    buf_size = parent.buffers[node.name].get_buf_len(name)
                    if buf_size > 0:
                        two_step_buffer_size[child][parent] = buf_size

        active_children = set(two_step_buffer_size.keys())
        if not active_children:
            return
        active_parents = set([k for (k,v) in curr_capacity.iteritems() if v > 0])

        while True:
            buf_size, parent, child = self._calc_max_buffer(node, active_parents, active_children, two_step_buffer_size)
            if buf_size == 0:
                return

            # Run odd even down hill
            output_size = output_buffer_size[child]

            if self.divide_by_fanout:
                output_size /= len(active_children)
                #output_size /= len(node.children)


            if self.check_odd_even_rule(buf_size, output_size):
                if child is not None:
                    self.to_send[parent, node, child.name] += 1
                else:
                    self.to_send[parent, node, LAST_STOP_BUFFER] += 1

                assert two_step_buffer_size[child][parent] > 0
                two_step_buffer_size[child][parent] -= 1

                assert curr_capacity[parent] > 0
                curr_capacity[parent] -= 1

                if curr_capacity[parent] == 0:
                    active_parents.remove(parent)

            else:
                active_children.remove(child)


    def run_forwarding_step(self):
        for (node, next_node, two_steps), count in self.to_send.iteritems():
            node.send(next_node.name, count, two_steps_node=two_steps)

    # Here we conserve the LIS behaviour
    def _calc_max_buffer_lis(self, node, active_parents, active_children, two_step_buffer_size):
        curr_max = 0
        max_parent = max_child = None
        min_packet_id = None

        for child in active_children:
            for parent in active_parents:
                try:
                    val = two_step_buffer_size[child][parent]
                except:
                    continue
                if val == 0:
                    continue
                if val == curr_max:
                    packet_id = parent.buffers[node.name].get_top_packet_id(child.name if child is not None else None)
                    if packet_id < min_packet_id:
                        max_parent, max_child, curr_max = parent, child, val
                        min_packet_id = packet_id
                elif val > curr_max:
                    max_parent, max_child, curr_max = parent, child, val
                    min_packet_id = parent.buffers[node.name].get_top_packet_id(child.name if child is not None else None)
        return curr_max, max_parent, max_child

    # Here we randomly select in case of equality
    def _calc_max_buffer_randomaly(self, node, active_parents, active_children, two_step_buffer_size):
        curr_max = 0
        max_parent = max_child = None
        n = 1
        for child in active_children:
            for parent in active_parents:
                try:
                    val = two_step_buffer_size[child][parent]
                except:
                    continue
                if val == 0:
                    continue
                update = False
                if val == curr_max:
                    n += 1
                    update = random.random() < 1./n
                if val > curr_max or update:
                    max_parent, max_child, curr_max = parent, child, val
        return curr_max, max_parent, max_child

    def check_odd_even_rule_orig(self, buf_size, output_size):
        odd_even_rule = (buf_size == output_size) and ((output_size % 2) == 1)
        return buf_size > output_size or odd_even_rule

    def check_odd_even_rule_greedy_fallback(self, buf_size, output_size):
        odd_even_rule = (buf_size == output_size) and ((output_size % 2) == 1)
        return buf_size > output_size or odd_even_rule or (random.random() < self.bypass_prob)