from rdflib import Graph

from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates, import_default_sw_ontologies
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_formula_translator import \
    translate_sw_triple_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_subformula_translator import \
    translate_sw_triple_to_fol_subformula


def translate_owl_ontology_to_fol_theory(owl_ontology: Graph):
    populate_default_predicates()
    import_default_sw_ontologies(rdf_graph=owl_ontology)
    for sw_triple in owl_ontology:
        Variable.clear_used_variable_letters()
        variables = [Variable.get_next_variable(),Variable.get_next_variable()]
        formula = translate_sw_triple_to_fol_subformula(sw_triple=sw_triple, rdf_graph=owl_ontology, variables=variables)
        if formula:
            FormulaOriginRegistry.parsed_sw_triples.add(sw_triple)
    for sw_triple in owl_ontology:
        if sw_triple not in FormulaOriginRegistry.parsed_sw_triples:
            Variable.clear_used_variable_letters()
            variables = [Variable.get_next_variable(),Variable.get_next_variable()]
            translate_sw_triple_to_fol_formula(sw_triple=sw_triple, rdf_graph=owl_ontology, variables=variables)
