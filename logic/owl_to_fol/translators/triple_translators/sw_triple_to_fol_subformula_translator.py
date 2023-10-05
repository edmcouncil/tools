from typing import Optional

from rdflib import Graph, RDF, OWL, XSD

from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.translators.triple_translators.owl_triple_to_fol_subformula_translator import \
    translate_owl_construct_to_fol_subformula
from logic.owl_to_fol.translators.triple_translators.rdf_triple_to_fol_subformula_translator import \
    translate_rdf_construct_to_fol_subformula
from logic.owl_to_fol.translators.triple_translators.sw_to_fol_translation_filterers import \
    is_triple_out_of_scope_for_direct_translation
from logic.owl_to_fol.translators.triple_translators.xsd_triple_to_fol_subformula_translator import \
    translate_xsd_construct_to_fol_subformula


def translate_sw_triple_to_fol_subformula(sw_triple: tuple, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    formula = None
    
    if is_triple_out_of_scope_for_direct_translation(sw_triple=sw_triple, rdf_graph=rdf_graph):
        return formula
    # if is_ignored_triple_in_direct_translation(sw_triple=sw_triple):
    #     return formula
    
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
    
    return formula