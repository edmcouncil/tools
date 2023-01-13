from pyshacl import validate
from rdflib import Graph

from shacl.data_model_generator import generate_shacl_model_from_ontology
from shacl.shacler import shacl

ontology = Graph()
ontology.parse('resources/idmp_master_v0.1.0/AboutIDMPDevMerged_v0.1.0.ttl')
generate_shacl_model_from_ontology(ontology=ontology)
shacled_ontology = shacl()
shacled_ontology.serialize('shacled.ttl')


r = validate(data_graph=ontology,
      shacl_graph=shacled_ontology,
      inference='rdfs',
      abort_on_first=False,
      allow_infos=True,
      allow_warnings=True,
      meta_shacl=False,
      advanced=True,
      js=False,
      debug=False)
conforms, results_graph, results_text = r
v=0