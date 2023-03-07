from rdflib import URIRef


class Symbol:
    def __init__(self, origin):
        self.origin = origin
        if isinstance(origin, URIRef):
            if '#' in str(self.origin):
                self.letter = origin.fragment
            else:
                self.letter = str(self.origin).split(sep='/')[-1]
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