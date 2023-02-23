from fol_logic.objects.propositional_formula import PropositionalFormula


class Equivalence(PropositionalFormula):
    def __init__(self, arguments: list):
        if not len(arguments) == 2:
            raise Exception('Wrong equivalence initialisation')
        super().__init__(arguments=arguments)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.bracketise(' '.join([self.arguments[0].get_tptp_axiom(), '<=>', self.arguments[1].get_tptp_axiom()]))
        return tptp_axiom
        
        