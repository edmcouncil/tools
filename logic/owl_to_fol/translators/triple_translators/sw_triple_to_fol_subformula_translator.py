from typing import Optional

from rdflib import Graph, RDF, OWL, XSD

from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.translators.triple_translators.owl_triple_to_fol_subformula_translator import \
    translate_owl_construct_to_fol_subformula
from logic.owl_to_fol.translators.triple_translators.rdf_triple_to_fol_subformula_translator import \
    translate_rdf_construct_to_fol_subformula
from logic.owl_to_fol.translators.triple_translators.sw_to_fol_helper import is_triple_out_of_scope, is_ignored_triple
from logic.owl_to_fol.translators.triple_translators.xsd_triple_to_fol_subformula_translator import \
    translate_xsd_construct_to_fol_subformula


def translate_sw_triple_to_fol_subformula(sw_triple: tuple, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    if is_triple_out_of_scope(sw_triple=sw_triple, rdf_graph=rdf_graph):
        return None
    
    if is_ignored_triple(sw_triple=sw_triple):
        return None
    
    # arguments = __get_arguments(sw_triple=sw_triple, owl_ontology=rdf_graph, variables=variables)
    sw_arguments = [sw_triple[0], sw_triple[2]]
    
    sw_predicate = sw_triple[1]
    if sw_predicate in XSD:
        formula = \
            translate_xsd_construct_to_fol_subformula(
                rdf_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables)
    elif sw_predicate in RDF:
        formula = \
            translate_rdf_construct_to_fol_subformula(
                rdf_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables,
                rdf_graph=rdf_graph)
    elif sw_predicate in OWL:
        formula = \
            translate_owl_construct_to_fol_subformula(
                owl_predicate=sw_predicate,
                sw_arguments=sw_arguments,
                variables=variables,
                rdf_graph=rdf_graph)
    else:
        return None
    
    return formula