from enum import Enum

from logic.objects.formula import Formula


class Quantifier(Enum):
    UNIVERSAL = 'all'
    EXISTENTIAL = 'some'

class QuantifyingFormula(Formula):
    
    def __init__(self, quantified_formula: Formula, variables: list, quantifier: Quantifier, is_self_standing=True):
        super().__init__(is_self_standing)
        self.quantified_formula = quantified_formula
        self.variables = variables
        self.quantifier = quantifier
        self.free_variables = self.get_free_variables()
        
    def get_tptp_axiom(self) -> str:
        if self.quantifier == Quantifier.UNIVERSAL:
            tptp_quantifier = '!'
        else:
            tptp_quantifier = '?'
        tptp_axiom = \
            ' '.join(
                [
                    tptp_quantifier,
                    '[', ','.join([str(variable).upper() for variable in self.variables]),
                    ']',
                    ':',
                    self.quantified_formula.get_tptp_axiom()])
        return self.bracketise(tptp_axiom)
    
    def get_free_variables(self):
        free_variables = set(self.quantified_formula.free_variables)
        for variable in self.variables:
            if variable in free_variables:
                free_variables.remove(variable)
        return free_variables
    
    
