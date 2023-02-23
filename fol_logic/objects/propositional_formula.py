from fol_logic.objects.formula import Formula


class PropositionalFormula(Formula):
    def __init__(self, arguments: list):
        super().__init__()
        self.arguments = arguments
        self.free_variables = self.get_free_variables()

    def get_free_variables(self) -> set:
        free_variables = set()
        for argument in self.arguments:
            free_variables = free_variables.union(argument.free_variables)
        return free_variables