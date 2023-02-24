from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term

TPTP_DEFAULT_LETTER = 'X'

class DefaultVariable(Term):
    registry = dict()
    
    def __init__(self):
        super().__init__(origin=None)
        
        
    def to_tptp(self):
        return TPTP_DEFAULT_LETTER