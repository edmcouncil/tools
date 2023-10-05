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
from logic.owl_to_fol.translators.triple_translators.sw_to_fol_translation_filterers import \
    is_triple_out_of_scope_for_direct_translation


def translate_sw_triple_to_fol_formula(sw_triple: tuple, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    if is_triple_out_of_scope_for_direct_translation(sw_triple=sw_triple, rdf_graph=rdf_graph):
        return None
    
    sw_arguments = [sw_triple[0], sw_triple[2]]
    sw_predicate = sw_triple[1]
    if sw_predicate in RDF:
        formula = \
            translate_rdf_construct_to_fol_formula(
                rdf_predicate=sw_predicate,
                sw_arguments=sw_arguments,
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
