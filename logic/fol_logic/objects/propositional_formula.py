from logic.fol_logic.objects.formula import Formula


class PropositionalFormula(Formula):
    def __init__(self, arguments: list, is_self_standing=False):
        self.arguments = arguments
        self.free_variables = self.get_free_variables()
        super().__init__(is_self_standing=is_self_standing)

    def get_free_variables(self) -> set:
        free_variables = set()
        for argument in self.arguments:
            free_variables = free_variables.union(argument.free_variables)
        return free_variables
    