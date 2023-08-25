from rdflib import Graph

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.translators.translator_helpers import get_fol_symbol_for_owl_node


def translate_custom_construct_to_self_standing_fol_formula(sw_triple: tuple, rdf_graph: Graph) -> Formula:
    triple_subject = get_fol_symbol_for_owl_node(node=sw_triple[0], rdf_graph=rdf_graph)
    triple_predicate = get_fol_symbol_for_owl_node(node=sw_triple[1], rdf_graph=rdf_graph, arity=2)
    triple_object = get_fol_symbol_for_owl_node(node=sw_triple[2], rdf_graph=rdf_graph)
    formula = AtomicFormula(predicate=triple_predicate, arguments=[triple_subject, triple_object], is_self_standing=True)
    return formula

