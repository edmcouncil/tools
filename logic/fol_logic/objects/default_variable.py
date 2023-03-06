from logic.fol_logic.objects.term import Term

TPTP_DEFAULT_LETTER_1 = 'X'
TPTP_DEFAULT_LETTER_2 = 'Y'
TPTP_DEFAULT_LETTER_3 = 'Z'

class DefaultVariable(Term):
    registry = dict()
    
    def __init__(self, letter=TPTP_DEFAULT_LETTER_1):
        super().__init__(origin=None)
        self.letter = letter
        
        
    def to_tptp(self):
        return self.letter
    
    def __repr__(self):
        return self.letter
    