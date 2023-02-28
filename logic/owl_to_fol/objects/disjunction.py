from logic.owl_to_fol.objects.propositional_formula import PropositionalFormula


class Disjunction(PropositionalFormula):
    def __init__(self, arguments: list):
        if len(arguments) < 2:
            raise Exception('Wrong disjunction initialisation')
        super().__init__(arguments=arguments)
        

    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.bracketise(' '.join([self.arguments[0].get_tptp_axiom(), '|', self.arguments[1].get_tptp_axiom()]))
        return tptp_axiom
        
    def __repr__(self):
        return '(' + ' '.join([self.arguments[0].__repr__() + ' or ' + self.arguments[1].__repr__()]) +')'