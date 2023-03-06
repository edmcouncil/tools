from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.identity import Identity
from logic.fol_logic.objects.predicate import Predicate


class IdentityFormula(AtomicFormula):
    
    def __init__(self, arguments: list, is_self_standing=True):
        super().__init__(predicate=Identity(), arguments=arguments, is_self_standing=is_self_standing)
        self.free_variables = set(self.arguments)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = '(' + ')'
        return tptp_axiom
    
    def __repr__(self):
        return ''.join([self.arguments[0].__repr__(), self.predicate.__repr__(), self.arguments[1].__repr__()])
    
