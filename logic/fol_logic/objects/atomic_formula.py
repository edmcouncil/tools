import logging

from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.term import Term


class AtomicFormula(Formula):
    
    def __init__(self, predicate: Predicate, arguments: list, is_self_standing=False):
        super().__init__(is_self_standing)
        self.predicate = predicate
        self.arguments = arguments
        self.free_variables = set(self.arguments)
        
    def swap_arguments(self, inplace=True):
        if inplace:
            self.arguments.reverse()
        else:
            reversed_arguments = self.arguments.copy()
            reversed_arguments.reverse()
            return AtomicFormula(predicate=self.predicate, arguments=reversed_arguments)
            
    def replace_arguments(self, arguments: list, inplace=False):
        if inplace:
            self.arguments = arguments
        else:
            return AtomicFormula(predicate=self.predicate, arguments=arguments,is_self_standing=self.is_self_standing)
        
    def replace_argument(self, argument: Term, index: int, inplace=False):
        if index > len(self.arguments):
            logging.error(msg='Index out of bounds for argument replacement')
            return
        replaced_arguments = self.arguments.copy()
        replaced_arguments[index] = argument
        if inplace:
            self.arguments = replaced_arguments
        else:
            return AtomicFormula(predicate=self.predicate, arguments=replaced_arguments,is_self_standing=self.is_self_standing)
        
    def get_tptp_axiom(self) -> str:
        tptp_axiom = self.predicate.to_tptp() +'(' +','.join([argument.to_tptp() for argument in self.arguments]) + ')'
        return tptp_axiom
    
    def __repr__(self):
        return ''.join([self.predicate.__repr__(), '(', ','.join([argument.__repr__() for argument in self.arguments]), ')'])
    
