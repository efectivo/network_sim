import patterns


class PatternComposite(patterns.PatternIfc):
    def __init__(self, C, create_pattern_func, pattern_dict):
        self.patterns = [create_pattern_func(pattern_dict) for _ in range(C)]

    def invoke(self, curr_cycle):
        out = []
        for pattern in self.patterns:
            out += pattern.invoke(curr_cycle)
        return out