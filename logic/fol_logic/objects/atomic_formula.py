import logging

from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.term import Term
from logic.fol_logic.objects.variable import Variable


class AtomicFormula(Formula):
    
    def __init__(self, predicate: Predicate, arguments: list, is_self_standing=False, tptp_type='fof'):
        super().__init__(is_self_standing, tptp_type=tptp_type)
        self.predicate = predicate
        self.arguments = arguments
        self.__set_free_variables()
        self.set_tptp_type()
            
    def __repr__(self):
        return ''.join([self.predicate.__repr__(), '(', ','.join([argument.__repr__() for argument in self.arguments]), ')'])
        
    def __set_free_variables(self):
        for argument in self.arguments:
            if isinstance(argument, Variable):
                self.free_variables.add(argument)
    
    def swap_arguments(self, inplace=False):
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
            return AtomicFormula(predicate=self.predicate, arguments=arguments, is_self_standing=self.is_self_standing)
        
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
    
    
    def replace_variable(self, old_variable: Variable, new_variable: Variable):
        arguments_copy = self.arguments.copy()
        for index in range(len(self.arguments)):
            if self.arguments[index] == old_variable:
                arguments_copy[index] = new_variable
        self.arguments = arguments_copy
        
    def set_tptp_type(self):
        for argument in self.arguments:
            if not argument.origin_type == str:
                self.tptp_type = 'tff'
                return
        
    
    
    
