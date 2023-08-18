import logging

from rdflib import OWL, URIRef

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.fol_logic.objects.symbol import Symbol
from logic.fol_logic.objects.variable import Variable


def translate_owl_construct_to_self_standing_fol_formula(owl_type: URIRef, arguments: list, variables: list):
    if owl_type in owl_to_fol_map:
        owl_to_fol_map[owl_type](arguments, variables)
    

def __translate_owl_inverse_of(arguments: list, variables: list):
    if not len(arguments) == 2:
        logging.exception(msg='Wrong number of owl:inverseOf arguments')
        return None
    argument1 = arguments[0]
    argument2 = arguments[1]
    if not isinstance(argument1, AtomicFormula):
        logging.exception(msg='Wrong type of first argument of owl:inverseOf')
        return None
    if not isinstance(argument2, AtomicFormula):
        logging.exception(msg='Wrong type of second argument of owl:inverseOf')
        return None
    inverse_argument2 = argument2.swap_arguments()
    inverse_formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, inverse_argument2]),
            variables=variables,
            quantifier=Quantifier.UNIVERSAL,
            is_self_standing=True)
    return inverse_formula

def __translate_owl_equivalent(arguments: list, variables: list):
    if not len(arguments) == 2:
        logging.exception(msg='Wrong number of owl:inverseOf arguments')
        return None
    argument1 = arguments[0]
    argument2 = arguments[1]
    QuantifyingFormula(
        quantified_formula=Equivalence(arguments=[argument1, argument2]),
        variables=variables,
        quantifier=Quantifier.UNIVERSAL,
        is_self_standing=True)

owl_to_fol_map = \
    {
        OWL.inverseOf : __translate_owl_inverse_of,
        OWL.equivalentClass: __translate_owl_equivalent
    }

