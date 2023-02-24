from logic.owl_to_fol.objects.symbol import Symbol


class Term(Symbol):
    registry = dict()
    
    def __init__(self, origin):
        super().__init__(origin)
        Term.registry[origin] = self
        
    def to_tptp(self):
        return self.origin