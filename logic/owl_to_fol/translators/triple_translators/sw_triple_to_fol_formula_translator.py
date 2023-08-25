from typing import Optional

from rdflib import Graph, RDF, RDFS, OWL

from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.translators.triple_translators.custom_triple_to_fol_formula_translator import \
    translate_custom_construct_to_self_standing_fol_formula
from logic.owl_to_fol.translators.triple_translators.owl_triple_to_fol_formula_translator import \
    translate_owl_construct_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.rdf_triple_to_fol_formula_translator import \
    translate_rdf_construct_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.rdfs_triple_to_fol_formula_translator import \
    translate_rdfs_construct_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.sw_to_fol_helper import is_triple_out_of_scope, is_ignored_triple


def translate_sw_triple_to_fol_formula(sw_triple: tuple, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    if is_triple_out_of_scope(sw_triple=sw_triple, rdf_graph=rdf_graph):
        return None
    
    if is_ignored_triple(sw_triple=sw_triple):
        return None
    
    # arguments = __get_arguments(sw_triple=sw_triple, owl_ontology=rdf_graph, variables=variables)
    sw_arguments = [sw_triple[0], sw_triple[2]]
    
    sw_predicate = sw_triple[1]
    if sw_predicate in RDF:
        formula = \
            translate_rdf_construct_to_fol_formula(
                rdf_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables,
                rdf_graph=rdf_graph)
    elif sw_predicate in RDFS:
        formula = \
            translate_rdfs_construct_to_fol_formula(
                rdfs_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables,
                rdf_graph=rdf_graph)
    elif sw_predicate in OWL:
        formula = \
            translate_owl_construct_to_fol_formula(
                owl_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables,
                rdf_graph=rdf_graph)
    else:
        formula = translate_custom_construct_to_self_standing_fol_formula(sw_triple=sw_triple, rdf_graph=rdf_graph)
    
    return formula

# def triple_is_of_of_scope(sw_triple: tuple) -> bool:
#     if sw_triple[1] == RDF.type and (sw_triple[2] in RDF or sw_triple[2] in RDFS or sw_triple[2] in OWL):
#         return True
#     if sw_triple[1] == OWL.deprecated:
#         return True
#
#     return False
    
#
# def __get_arguments(sw_triple: tuple, owl_ontology: Graph, variables: list) -> Optional[list]:
#     sw_triple_subject = sw_triple[0]
#     subject_argument = get_subformula_from_node(node=sw_triple_subject, rdf_graph=owl_ontology, variables=variables)
#     if not subject_argument:
#         subject_argument = sw_triple_subject
#     sw_triple_object = sw_triple[2]
#     object_argument = get_subformula_from_node(node=sw_triple_object, rdf_graph=owl_ontology, variables=variables)
#     if not object_argument:
#         object_argument = sw_triple_object
#     return [subject_argument, object_argument]