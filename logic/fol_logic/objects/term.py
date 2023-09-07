from typing import Union

from logic.fol_logic.objects.symbol import Symbol


class Term(Symbol):
    registry = dict()
    
    def __init__(self, origin_value:object, origin_type=str):
        super().__init__(origin_value=origin_value, origin_type=origin_type)
        Term.registry[origin_value] = self
        
    def to_tptp(self):
        if self.origin_type == str:
            tptp_term = self.value.lower()
            tptp_term = Symbol.escape_tptp_chars(text=tptp_term)
        else:
            tptp_term = self.value
        return tptp_term
