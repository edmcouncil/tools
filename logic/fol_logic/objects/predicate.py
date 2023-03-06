from rdflib import URIRef

from logic.fol_logic.objects.symbol import Symbol


class Predicate(Symbol):
    registry = dict()
    
    def __init__(self, arity: int, origin=str()):
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
    