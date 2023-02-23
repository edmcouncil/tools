import uuid

from owl_to_fol.objects.atomic_formula import AtomicFormula
from owl_to_fol.objects.predicate import Predicate


class IdentityFormula(AtomicFormula):
    
    def __init__(self, predicate: Predicate, arguments: list, is_self_standing=True):
        super().__init__(predicate=predicate, arguments=arguments, is_self_standing=is_self_standing)
        self.free_variables = set(self.arguments)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = '(' + ')'
        return tptp_axiom
    
