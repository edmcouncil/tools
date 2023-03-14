from logic.fol_logic.objects.symbol import Symbol


class Term(Symbol):
    registry = dict()
    
    def __init__(self, origin):
        super().__init__(origin)
        Term.registry[origin] = self
        
    def to_tptp(self):
        tptp_term = self.letter.lower()
        tptp_term = tptp_term.replace('-', '_')
        tptp_term = tptp_term.replace('.', '_')
        tptp_term = tptp_term.replace('/', '_')
        tptp_term = tptp_term.replace(':', '_')
        tptp_term = tptp_term.replace('?', '_')
        tptp_term = tptp_term.replace('=', '_')
        tptp_term = tptp_term.replace('%', '_')
        tptp_term = tptp_term.replace('&', '_')
        tptp_term = tptp_term.replace('|', '_')
        tptp_term = tptp_term.replace("'", '_')
        tptp_term = tptp_term.replace('"', '_')
        if tptp_term[0].isdigit():
            tptp_term = 'node_' + tptp_term
        return tptp_term
