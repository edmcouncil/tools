from logic.owl_to_fol.objects.predicate import Predicate
from logic.owl_to_fol.objects.symbol import Symbol


class Identity(Predicate):
    
    def __init__(self):
        super().__init__(origin=None, arity=2)

    def to_tptp(self):
        return '='
    
    def __repr__(self):
        return '='