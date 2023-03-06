import uuid


class Formula():
    registry = set()
    
    def __init__(self, is_self_standing=False, is_fol=True):
        self.is_self_standing = is_self_standing
        self.is_fol = is_fol
        self.free_variables = set()
        Formula.registry.add(self)
    
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
            
            tptp_formula = 'fof' + '(' + ' axiom' + str(uuid.uuid4()).replace('-','') + ',' + 'axiom' + ',' + tptp_axiom + ')' + '.'
            return tptp_formula
        else:
            return tptp_axiom
    
    def get_tptp_axiom(self) -> str:
        pass
    
    def bracketise(self, formula: str):
        return '(' + formula + ')'