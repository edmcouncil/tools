from logic.fol_logic.objects.propositional_formula import PropositionalFormula


class Negation(PropositionalFormula):
    def __init__(self, arguments: list, is_self_standing=False):
        if not len(arguments) == 1:
            raise Exception('Wrong negation initialisation')
        super().__init__(arguments=arguments, is_self_standing=is_self_standing)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.bracketise('~' + self.arguments[0].get_tptp_axiom())
        return tptp_axiom
    
    def __repr__(self):
        return 'not' + Negation.bracketise(self.arguments[0].__repr__())