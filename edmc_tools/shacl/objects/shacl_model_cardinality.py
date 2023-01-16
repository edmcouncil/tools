from rdflib import Literal


class ShaclModelCardinality:
    def __init__(self, max=-1, min=-1):
        if isinstance(max, Literal):
            self.max = max.value
        else:
            self.max = max
        if isinstance(min, Literal):
            self.min = min.value
        else:
            self.min = min