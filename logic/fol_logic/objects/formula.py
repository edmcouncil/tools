import copy
import uuid

from logic.fol_logic.objects.variable import Variable


class Formula(object):
    registry = list()
    
    def __init__(self, is_self_standing=False, tptp_type='fof'):
        self.is_self_standing = is_self_standing
        self.tptp_type = tptp_type
        self.free_variables = set()
        if is_self_standing:
            Formula.registry.append(self)
    
    def to_tptp(self) -> str:
        tptp_axiom = self.get_tptp_axiom()

        if self.is_self_standing:
            if len(self.free_variables) > 0:
                tptp_axiom_quantification_closure = \
                    ' '.join(
                        [
                            '!',
                            '[', ','.join([str(variable).upper() for variable in self.free_variables]),
                            ']',
                            ':'
                        ])
                tptp_axiom = tptp_axiom_quantification_closure + '(' + tptp_axiom + ')'
            
            tptp_formula = self.tptp_type + '(' + ' axiom' + str(uuid.uuid4()).replace('-','') + ',' + 'axiom' + ',' + tptp_axiom + ')' + '.'
            return tptp_formula
        else:
            return tptp_axiom
    
    def get_tptp_axiom(self) -> str:
        pass
    
    @staticmethod
    def bracketise(formula: str):
        return '(' + formula + ')'
    
    def replace_free_variable(self, old_variable: Variable, new_variable: Variable):
        for free_variable in self.free_variables:
            if free_variable == old_variable:
                self.replace_variable(old_variable=old_variable, new_variable=new_variable)
                
    def replace_variable(self, old_variable: Variable, new_variable: Variable):
        if hasattr(self, 'arguments'):
            for argument in self.arguments:
                argument.replace_variable(old_variable=old_variable, new_variable=new_variable)
    
    
    def copy(self):
        return copy.deepcopy(self)
    
    def set_tptp_type(self):
        pass