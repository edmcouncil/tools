from logic.fol_logic.objects.propositional_formula import PropositionalFormula


class Disjunction(PropositionalFormula):
    def __init__(self, arguments: list, is_self_standing=False):
        if len(arguments) < 2:
            raise Exception('Wrong disjunction initialisation')
        super().__init__(arguments=arguments, is_self_standing=is_self_standing)

    def get_tptp_axiom(self) -> str:
        # tptp_axiom = self.bracketise(' '.join([self.arguments[0].get_tptp_axiom(), '|', self.arguments[1].get_tptp_axiom()]))
        tptp_axiom = self.bracketise(' | '.join([argument.get_tptp_axiom() for argument in self.arguments]))
        return tptp_axiom
        
    def __repr__(self):
        return Disjunction.bracketise(' or '.join([argument.__repr__() for argument in self.arguments]))