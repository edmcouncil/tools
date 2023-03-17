from logic.fol_logic.objects.term import Term

DEFAULT_LETTER_1 = 'X'
DEFAULT_LETTER_2 = 'Y'
DEFAULT_LETTER_3 = 'Z'

class Variable(Term):
    registry = dict()
    
    def __init__(self, letter=DEFAULT_LETTER_1):
        super().__init__(origin=letter)

    def to_tptp(self):
        return self.letter.upper()
    
    def __repr__(self):
        return self.letter
    