from rdflib import Graph

from logic.owl_to_fol.owl_ontology_to_fol_theory_translator import translate_owl_ontology_to_fol_theory

iof = Graph()
iof.parse('/Users/pawel.garbacz/Documents/edmc/github/edmc/tools/resources/iof/dev.iof-quickstart.ttl')
rdf = Graph()
rdf.parse('http://www.w3.org/1999/02/22-rdf-syntax-ns')
rdfs = Graph()
rdfs.parse('http://www.w3.org/2000/01/rdf-schema')
owl = Graph()
owl.parse('http://www.w3.org/2002/07/owl')
translate_owl_ontology_to_fol_theory(owl_ontology=iof + rdf + rdfs + owl)