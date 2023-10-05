import logging

from rdflib import Graph

from logic.fol_logic.objects.identity_formula import IdentityFormula
from logic.fol_logic.objects.negation import Negation
from logic.fol_logic.objects.variable import Variable
from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates, import_default_sw_ontologies
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.triple_translators.sw_to_fol_translation_filterers import \
    is_triple_out_of_scope_for_direct_translation
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_formula_translator import \
    translate_sw_triple_to_fol_formula
from logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_subformula_translator import \
    translate_sw_triple_to_fol_subformula


def translate_rdf_graph_to_fol_theory(rdf_graph: Graph):
    populate_default_predicates()
    import_default_sw_ontologies(rdf_graph=rdf_graph)
    __translate_sw_triples(rdf_graph=rdf_graph)
    __add_diffs_for_literals()
    
    
def __translate_sw_triples(rdf_graph: Graph):
    for sw_triple in rdf_graph:
        Variable.clear_used_variable_letters()
        variables = [Variable.get_next_variable(),Variable.get_next_variable()]
        formula = translate_sw_triple_to_fol_subformula(sw_triple=sw_triple, rdf_graph=rdf_graph, variables=variables)
        if formula:
            FormulaOriginRegistry.parsed_sw_triples.add(sw_triple)
    for sw_triple in rdf_graph:
        if sw_triple not in FormulaOriginRegistry.parsed_sw_triples:
            Variable.clear_used_variable_letters()
            variables = [Variable.get_next_variable(),Variable.get_next_variable()]
            formula = translate_sw_triple_to_fol_formula(sw_triple=sw_triple, rdf_graph=rdf_graph, variables=variables)
            if formula:
                FormulaOriginRegistry.parsed_sw_triples.add(sw_triple)
                
                
def compare_owl_to_fol(rdf_graph: Graph):
    for sw_triple in rdf_graph:
        if not sw_triple in FormulaOriginRegistry.parsed_sw_triples:
            if not is_triple_out_of_scope_for_direct_translation(sw_triple=sw_triple, rdf_graph=rdf_graph):
                logging.warning(msg='Inscope triple ' + '|'.join(sw_triple) + ' was not parsed.')
                

def __add_diffs_for_literals():
    print(len(FormulaOriginRegistry.literals_map.values()))
    return 
    for literal_formula1 in FormulaOriginRegistry.literals_map.values():
        for literal_formula2 in FormulaOriginRegistry.literals_map.values():
            if not literal_formula1 == literal_formula2:
                Negation(
                    arguments=[IdentityFormula(arguments=[literal_formula1, literal_formula2])],
                    is_self_standing=True)
            
    