import logging
from typing import Optional

from rdflib import URIRef, Graph, BNode, RDF, OWL, RDFS
from rdflib.term import Node

import \
    logic.owl_to_fol.translators.triple_translators.sw_to_fol_translation_filterers as sw_to_fol_translation_filterers
import \
    logic.owl_to_fol.translators.triple_translators.sw_triple_to_fol_subformula_translator as sw_to_fol_subformula_translator
from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.term import Term
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.node_translators.owl_restriction_translator import generate_fol_from_owl_restriction
from logic.owl_to_fol.translators.node_translators.rdfs_datatype_restriction_translator import \
    translate_datatype_description
from logic.owl_to_fol.translators.translator_helpers import __can_uri_be_cast_to_unary_predicate, \
    __can_uri_be_cast_to_binary_predicate, __can_uri_be_cast_to_term, get_fol_symbol_for_owl_node


def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variables: list) -> Formula:
    if __can_uri_be_cast_to_unary_predicate(uri=uri, rdf_graph=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin_value=uri, arity=1)
        return \
            AtomicFormula(predicate=predicate, arguments=variables[:1])
    
    if __can_uri_be_cast_to_binary_predicate(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin_value=uri, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=variables)
    
    if __can_uri_be_cast_to_term(uri=uri, owl_ontology=owl_ontology):
        if uri in Term.registry:
            term = Term.registry[uri]
        else:
            term = Term(origin_value=uri)
        return term
    
    logging.warning(msg='Cannot get formula from ' + str(uri))


def get_subformula_from_node(node: Node, rdf_graph: Graph, variables: list) -> Optional[Formula]:
    if isinstance(node, BNode):
        return get_subformula_from_bnode(bnode=node, rdf_graph=rdf_graph, variables=variables)
    if isinstance(node, URIRef):
        return get_subformula_from_uri(uri=node, owl_ontology=rdf_graph, variables=variables)


def get_subformula_from_bnode(bnode: BNode, rdf_graph: Graph, variables: list) -> Formula:
    bnode_predictes_objects = list(rdf_graph.predicate_objects(subject=bnode))
    bnode_inscope_triples = list()
    for bnode_predicte, bnode_object in bnode_predictes_objects:
        if not sw_to_fol_translation_filterers.is_triple_out_of_scope_for_direct_translation(sw_triple=(bnode, bnode_predicte, bnode_object), rdf_graph=rdf_graph):
            bnode_inscope_triples.append((bnode, bnode_predicte, bnode_object))
            
    if len(bnode_inscope_triples) == 1:
        formula = sw_to_fol_subformula_translator.translate_sw_triple_to_fol_subformula(sw_triple=bnode_inscope_triples[0],rdf_graph=rdf_graph,variables=variables)
        return formula
    else:
        if (bnode, RDF.type, OWL.Restriction) in rdf_graph:
            formula = generate_fol_from_owl_restriction(owl_restriction=bnode, rdf_graph=rdf_graph, variables=variables)
            FormulaOriginRegistry.sw_to_fol_map[bnode] = formula
            return formula
        if (bnode, RDF.type, RDFS.Datatype) in rdf_graph:
            formula = translate_datatype_description(sw_datatype_description=bnode, rdf_graph=rdf_graph, variables=variables)
            return formula
        
        logging.warning(msg='Cannot process bnode: ' + str(bnode))


def get_fol_formulae_from_rdf_list(rdf_list_object: Node, rdf_graph: Graph, variables: list, fol_formulae: list) -> list:
    first_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return fol_formulae
    fol_formula = get_subformula_from_node(node=first_items_in_rdf_list[0], rdf_graph=rdf_graph, variables=variables)
    fol_formulae.append(fol_formula)
    rest_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.rest))
    fol_formulae = get_fol_formulae_from_rdf_list(rdf_list_object=rest_items_in_rdf_list[0], rdf_graph=rdf_graph, fol_formulae=fol_formulae, variables=variables)
    return fol_formulae


def get_fol_terms_from_rdf_list(rdf_list_object: Node, rdf_graph: Graph, fol_terms: list) -> list:
    first_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return fol_terms
    fol_term = get_fol_symbol_for_owl_node(node=first_items_in_rdf_list[0], rdf_graph=rdf_graph)
    fol_terms.append(fol_term)
    rest_items_in_rdf_list = list(rdf_graph.objects(subject=rdf_list_object, predicate=RDF.rest))
    fol_terms = get_fol_terms_from_rdf_list(rdf_list_object=rest_items_in_rdf_list[0], rdf_graph=rdf_graph, fol_terms=fol_terms)
    return fol_terms



