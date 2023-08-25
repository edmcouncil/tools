from rdflib import OWL, URIRef, Graph

from logic.fol_logic.objects.disjunction import Disjunction
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.sw_node_to_fol_translator import get_fol_formulae_from_rdf_list, \
    get_fol_terms_from_rdf_list


def translate_owl_construct_to_fol_subformula(owl_predicate: URIRef, sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    match owl_predicate:
        case OWL.unionOf:
            return __translate_unionof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)
        case OWL.oneOf:
            return __translate_oneof(sw_arguments=sw_arguments, rdf_graph=rdf_graph, variables=variables)

        
def __translate_unionof(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    unioned_fol_formulae = get_fol_formulae_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph, variables=variables, fol_formulae=list())
    formula = Disjunction(arguments=unioned_fol_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]] = formula
    return formula


def __translate_oneof(sw_arguments: list, rdf_graph: Graph, variables: list) -> Formula:
    fol_terms = get_fol_terms_from_rdf_list(rdf_list_object=sw_arguments[1], rdf_graph=rdf_graph,fol_terms=list())
    variable = variables[0]
    identify_formulae = list()
    for fol_term in fol_terms:
        identity_formula = IdentityFormula(arguments=[variable, fol_term])
        identify_formulae.append(identity_formula)
    formula = Disjunction(arguments=identify_formulae)
    FormulaOriginRegistry.sw_to_fol_map[sw_arguments[1]] = formula
    return formula
