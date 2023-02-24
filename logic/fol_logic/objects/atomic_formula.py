from logic.fol_logic.objects.formula import Formula


class AtomicFormula(Formula):
    
    def __init__(self, predicate: str, variables: list, is_self_standing=True):
        super().__init__(is_self_standing)
        self.predicate = predicate
        self.variables = variables
        self.free_variables = set(self.variables)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.predicate.lower()+'('+','.join([str(variable).upper() for variable in self.variables]) + ')'
        return tptp_axiom
    
    
