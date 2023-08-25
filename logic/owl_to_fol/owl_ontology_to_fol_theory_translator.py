from rdflib import Graph

from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_formula_translator import \
    translate_sw_triple_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_subformula_translator import \
    translate_sw_triple_to_fol_subformula


def translate_owl_ontology_to_fol_theory(owl_ontology: Graph):
    populate_default_predicates()
    for sw_triple in owl_ontology:
        Variable.clear_used_variable_letters()
        variables = [Variable(letter=Variable.get_next_variable_letter()),Variable(letter=Variable.get_next_variable_letter())]
        translate_sw_triple_to_fol_subformula(sw_triple=sw_triple, rdf_graph=owl_ontology, variables=variables)
    for sw_triple in owl_ontology:
        Variable.clear_used_variable_letters()
        variables = [Variable(letter=Variable.get_next_variable_letter()),Variable(letter=Variable.get_next_variable_letter())]
        translate_sw_triple_to_fol_formula(sw_triple=sw_triple, rdf_graph=owl_ontology, variables=variables)
