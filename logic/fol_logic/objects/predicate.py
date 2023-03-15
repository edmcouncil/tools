import re

from rdflib import URIRef

from logic.fol_logic.objects.symbol import Symbol


class Predicate(Symbol):
    registry = dict()
    
    def __init__(self, arity: int, origin=str()):
        super().__init__(origin)
        self.arity = arity
        Predicate.registry[origin] = self
        
            
    def to_tptp(self):
        tptp_predicate = self.letter.lower()
        tptp_predicate = tptp_predicate.replace('-','_')
        tptp_predicate = tptp_predicate.replace('.', '_')
        tptp_predicate = re.sub(r'[^\x00-\x7F]+', '_', tptp_predicate)
        return tptp_predicate
    