class Symbol:
    def __init__(self, origin):
        self.origin = origin
        self.letter = origin
        
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