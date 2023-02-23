import uuid


class Formula():
    registry = set()
    
    def __init__(self, is_self_standing=True):
        self.is_self_standing = is_self_standing
        Formula.registry.add(self)
        self.free_variables = set()
    
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