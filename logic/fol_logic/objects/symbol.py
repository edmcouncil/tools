from rdflib import URIRef


class Symbol:
    def __init__(self, origin):
        self.origin = origin
        if isinstance(origin, URIRef):
            if '#' in str(self.origin):
                self.letter = origin.fragment
            else:
                # self.letter = str(self.origin).split(sep='/')[-1]
                origin_fragments = str(self.origin).split(sep='/')
                origin_fragments.reverse()
                for origin_fragment in origin_fragments:
                    if len(origin_fragment) > 0:
                        self.letter = origin_fragment
                        return
        else:
            self.letter = str(origin)
        
    def to_tptp(self):
        pass
        
    def __repr__(self):
        return self.letter
    
    def __eq__(self, other):
        if isinstance(other, Symbol):
            return self.letter == other.letter
        if isinstance(other, str):
            return self.letter == other
    
    def __hash__(self):
        return self.letter.__hash__()