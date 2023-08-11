import logging

from rdflib import Graph

from logic.fol_logic.objects.formula import Formula
from logic.owl_to_fol.owl_ontology_to_fol_theory_translator import translate_owl_ontology_to_fol_theory

logging.basicConfig(format='%(message)s', level=logging.WARN, datefmt='%m/%d/%Y %I:%M:%S %p', filename='iof_axioms.log')
fibo = Graph()
fibo.parse('../resources/fibo/fibo.ttl')


translate_owl_ontology_to_fol_theory(owl_ontology=fibo)

f = open('fibo_axioms.tptp', mode='w')
for formula in Formula.registry:
    if formula.is_self_standing:
        f.write(formula.to_tptp())
        f.write('\n')
f.close()