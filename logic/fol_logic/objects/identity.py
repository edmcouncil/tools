from logic.fol_logic.objects.predicate import Predicate


class Identity(Predicate):
    
    def __init__(self):
        super().__init__(origin=None, arity=2)

    def to_tptp(self):
        return '='
    
    def __repr__(self):
        return '='