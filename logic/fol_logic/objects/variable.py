from logic.fol_logic.objects.term import Term

DEFAULT_LETTER_1 = 'X'
DEFAULT_LETTER_2 = 'Y'
DEFAULT_LETTER_3 = 'Z'

DEFAULT_LETTERS = [DEFAULT_LETTER_1, DEFAULT_LETTER_2, DEFAULT_LETTER_3]

class Variable(Term):
    registry = dict()
    used_variable_letters = list()
    last_user_variable_index = 0
    
    @staticmethod
    def get_next_variable_letter():
        if len(Variable.used_variable_letters) < len(DEFAULT_LETTERS):
            next_variable_letter = DEFAULT_LETTERS[len(Variable.used_variable_letters)]
        else:
            Variable.last_user_variable_index += 1
            next_variable_letter = DEFAULT_LETTERS[-1] + str(Variable.last_user_variable_index)
        Variable.used_variable_letters.append(next_variable_letter)
        return next_variable_letter
    
    @staticmethod
    def clear_used_variable_letters():
        Variable.used_variable_letters.clear()
        Variable.last_user_variable_index = 0
    
    
    def __init__(self, letter=DEFAULT_LETTER_1):
        super().__init__(origin=letter)
        if letter not in Variable.used_variable_letters:
            Variable.used_variable_letters.append(letter)
            Variable.last_user_variable_index += 1

    def to_tptp(self):
        return self.letter.upper()
    
    def __repr__(self):
        return self.letter
    