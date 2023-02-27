from logic.owl_to_fol.objects.formula import Formula
from logic.owl_to_fol.objects.predicate import Predicate


class AtomicFormula(Formula):
    
    def __init__(self, predicate: Predicate, arguments: list, is_self_standing=True):
        super().__init__(is_self_standing)
        self.predicate = predicate
        self.arguments = arguments
        self.free_variables = set(self.arguments)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.predicate.origin.lower() +'(' +','.join([str(variable).upper() for variable in self.arguments]) + ')'
        return tptp_axiom
    
    def __repr__(self):
        return ''.join([self.predicate.__repr__(), '(', ','.join([argument.__repr__() for argument in self.arguments]), ')'])
    
