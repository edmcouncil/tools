from rdflib import Graph

from shacl.data_model_generator import generate_shacl_model_from_ontology
from shacl.shacler import shacl
from shacl.validator import validate_graph_with_shacl

ontology = Graph()
ontology.parse('../resources/idmp_current/dev.idmp-quickstart.ttl')
generate_shacl_model_from_ontology(ontology=ontology)
shacled_ontology = shacl()
shacled_ontology.serialize('shacled_idmp_current.ttl')
validate_graph_with_shacl(
    graph=ontology,
    shacl=shacled_ontology,
    results_file_path='../resources/idmp_current/AboutIDMPDevSHACLed_current.xlsx')