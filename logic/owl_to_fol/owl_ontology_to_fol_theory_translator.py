import logging

from rdflib import Graph

from logic.owl_to_fol.owl_to_fol_preparer import populate_default_predicates
from logic.owl_to_fol.translators.owl_triple_to_fol_translator import translate_rdf_triple_to_fol


def translate_owl_ontology_to_fol_theory(owl_ontology:Graph):
    logging.info(msg='Importing W3C ontologies')
    rdf = Graph()
    rdf.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns')
    rdfs = Graph()
    rdfs.parse('http://www.w3.org/2000/01/rdf-schema')
    owl = Graph()
    owl.parse('http://www.w3.org/2002/07/owl')
    owl_ontology = owl_ontology + rdf + rdfs + owl
    populate_default_predicates()
    for rdf_triple in owl_ontology:
        translate_rdf_triple_to_fol(rdf_triple=rdf_triple, owl_ontology=owl_ontology)
    v=0