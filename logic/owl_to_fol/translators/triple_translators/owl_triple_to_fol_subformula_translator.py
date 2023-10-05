import logging

from rdflib import OWL, URIRef, Graph

import logic.owl_to_fol.translators.node_translators.sw_node_to_fol_translator as sw_node_to_fol_translator
from logic.fol_logic.objects.conjunction import Conjunction
from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.equivalence import Equivalence
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.quantifying_formula import QuantifyingFormula, Quantifier
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry


def translate_owl_construct_to_fol_subformula(owl_predicate: URIRef, sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    match owl_predicate:
        case OWL.complementOf:
            return __translate_complementof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.unionOf:
            return __translate_unionof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.intersectionOf:
            return __translate_intersectionof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.oneOf:
            return translate_oneOf(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.distinctMembers:
            return __translate_distinctMembers(sw_arguments=sw_arguments, rdf_graph=rdf_graph)
        case OWL.equivalentProperty:
            return __translate_equivalentPropertyof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)

        
def __translate_unionof(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    unioned_fol_formulae = sw_node_to_fol_translator.get_fol_formulae_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, variables=variables, fol_formulae=list())
    formula = Disjunction(arguments=unioned_fol_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]] = formula
    return formula


def __translate_intersectionof(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    intesectioned_fol_formulae = sw_node_to_fol_translator.get_fol_formulae_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, variables=variables, fol_formulae=list())
    if None in intesectioned_fol_formulae:
        logging.warning(msg='Cannot process owl intersection for: ' + '|'.join(sw_arguments))
        return
    formula = Conjunction(arguments=intesectioned_fol_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]] = formula
    return formula


def __translate_complementof(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    complemented_fol_formulae = sw_node_to_fol_translator.get_fol_formulae_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, variables=variables, fol_formulae=list())
    formula = Negation(arguments=complemented_fol_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]] = formula
    return formula


def translate_oneOf(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    fol_terms = sw_node_to_fol_translator.get_fol_terms_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, fol_terms=list())
    variable = variables[0]
    identify_formulae = list()
    for fol_term in fol_terms:
        identity_formula = IdentityFormula(arguments=[variable, fol_term])
        identify_formulae.append(identity_formula)
    formula = Disjunction(arguments=identify_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]] = formula
    return formula


def __translate_distinctMembers(sw_arguments: list, rdf_graph: Graph) -> Formula:
    fol_terms = sw_node_to_fol_translator.get_fol_terms_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, fol_terms=list())
    difference_formulae = list()
    for fol_term1 in fol_terms:
        for fol_term2 in fol_terms:
            if not fol_term1 == fol_term2:
                difference_formula = Negation(arguments=[IdentityFormula(arguments=[fol_term1, fol_term2])])
                difference_formulae.append(difference_formula)
    formula = Conjunction(arguments=difference_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[0]] = formula
    return formula


def __translate_equivalentPropertyof(sw_arguments: list, variables: list, rdf_graph: Graph) -> Formula:
    argument1 = sw_node_to_fol_translator.get_subformula_from_node(node=sw_arguments[0], rdf_graph=rdf_graph, variables=variables)
    argument2 = sw_node_to_fol_translator.get_subformula_from_node(node=sw_arguments[1], rdf_graph=rdf_graph, variables=variables)
    formula = \
        QuantifyingFormula(
            quantified_formula=Equivalence(arguments=[argument1, argument2]),
            variables=variables,
            quantifier=Quantifier.EXISTENTIAL)
    return formula
