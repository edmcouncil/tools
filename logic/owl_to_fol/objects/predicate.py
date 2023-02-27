from rdflib import URIRef

from logic.owl_to_fol.objects.symbol import Symbol


class Predicate(Symbol):
    registry = dict()
    
    def __init__(self, origin, arity: int):
        super().__init__(origin)
        self.arity = arity
        Predicate.registry[origin] = self
        if isinstance(origin, URIRef):
            if '#' in str(self.origin):
                self.letter = origin.fragment
            else:
                self.letter = str(self.origin).split(sep='/')[-1]
        else:
            self.letter = str(origin)
        
    def __repr__(self):
        return str(self.letter)