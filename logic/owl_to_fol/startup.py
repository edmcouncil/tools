import logging

from rdflib import Graph

from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.owl_ontology_to_fol_theory_translator import translate_rdf_graph_to_fol_theory

logging.basicConfig(format='%(message)s', level=logging.WARN, datefmt='%m/%d/%Y %I:%M:%S %p', filename='iof_axioms.log')
fibo = Graph()
fibo.parse('../resources/fibo/fibo.ttl')

translate_rdf_graph_to_fol_theory(rdf_graph=fibo)
# compare_owl_to_fol(owl_ontology=fibo)

with open(file='fibo_axioms.tptp', mode='w') as file:
    for formula in Formula.registry:
        if formula.tptp_type == 'fof':
            file.write(formula.to_tptp())
            file.write('\n')


