from logic.fol_logic.objects.formula import Formula


class PropositionalFormula(Formula):
    def __init__(self, arguments: list, is_self_standing=False):
        super().__init__(is_self_standing=is_self_standing)
        self.arguments = arguments
        self.free_variables = self.get_free_variables()
        self.set_tptp_type()

    def get_free_variables(self) -> set:
        free_variables = set()
        for argument in self.arguments:
            if hasattr(argument, 'free_variables'):
                free_variables = free_variables.union(argument.free_variables)
        return free_variables
    
    def set_tptp_type(self):
        for argument in self.arguments:
            if argument.tptp_type == 'tff':
                self.tptp_type = 'tff'
                return
    