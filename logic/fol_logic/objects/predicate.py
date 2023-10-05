from logic.fol_logic.objects.symbol import Symbol


class Predicate(Symbol):
    registry = dict()
    
    def __init__(self, arity: int, origin_value=str(), tptp=str()):
        super().__init__(origin_value)
        self.arity = arity
        if len(tptp) > 0:
            self.tptp = tptp
        else:
            self.tptp = None
        Predicate.registry[origin_value] = self
        
            
    def to_tptp(self):
        if self.tptp:
            return self.tptp
        tptp_predicate = self.value.lower()
        tptp_predicate = Symbol.escape_tptp_chars(text=tptp_predicate)
        return tptp_predicate
    
ARITHMETIC_LESS_PREDICATE = Predicate(arity=2, tptp='$less', origin_value='<')
ARITHMETIC_GREATER_PREDICATE = Predicate(arity=2, tptp='$greater', origin_value='>')
ARITHMETIC_LESSEQ_PREDICATE = Predicate(arity=2, tptp='lesseq', origin_value='<=')
ARITHMETIC_GREATEREQ_PREDICATE = Predicate(arity=2, tptp='$greatereq', origin_value='>=')