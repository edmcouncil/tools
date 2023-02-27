from logic.owl_to_fol.objects.symbol import Symbol
from logic.owl_to_fol.objects.term import Term

TPTP_DEFAULT_LETTER_1 = 'X'
TPTP_DEFAULT_LETTER_2 = 'Y'

class DefaultVariable(Term):
    registry = dict()
    
    def __init__(self, letter=TPTP_DEFAULT_LETTER_1):
        super().__init__(origin=None)
        self.letter = letter
        
        
    def to_tptp(self):
        return self.letter
    
    def __repr__(self):
        return self.letter