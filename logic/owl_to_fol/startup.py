import logging

from rdflib import Graph

from logic.owl_to_fol.owl_ontology_to_fol_theory_translator import translate_owl_ontology_to_fol_theory

logging.basicConfig(format='%(message)s', level=logging.WARN, datefmt='%m/%d/%Y %I:%M:%S %p', filename='iof_axioms.log')
fibo = Graph()
fibo.parse('../resources/fibo/fibo.ttl')


translate_owl_ontology_to_fol_theory(owl_ontology=fibo)
