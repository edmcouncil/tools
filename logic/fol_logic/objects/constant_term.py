from logic.fol_logic.objects.term import Term


class ConstantTerm(Term):
    registry = dict()
    
    def __init__(self, origin_value: object, origin_type=str):
        super().__init__(origin_value=origin_value, origin_type=origin_type)
        Term.registry[origin_value] = self
    
    # def to_tptp(self):
    #     tptp_term = self.value.lower()
    #     tptp_term = Symbol.escape_tptp_chars(text=tptp_term)
    #     if len(tptp_term) == 0:
    #         tptp_term = "' '"
    #     if tptp_term[0].isdigit():
    #         tptp_term = 'node_' + tptp_term
    #     return tptp_term