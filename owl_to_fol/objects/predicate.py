from owl_to_fol.objects.symbol import Symbol


class Predicate(Symbol):
    registry = dict()
    
    def __init__(self, origin, arity: int):
        super().__init__(origin)
        self.arity = arity
        Predicate.registry[origin] = self