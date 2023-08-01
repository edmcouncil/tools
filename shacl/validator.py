from pyshacl import validate
from rdflib import Graph

data_graph = Graph().parse('https://spec.edmcouncil.org/idmp/ontology/master/latest/dev.idmp-quickstart.ttl')
shacl_graph = Graph().parse('https://spec.pistoiaalliance.org/idmp/ontology/AboutIDMPDev-ReferenceIndividuals-SHACL.ttl')


conforms, results_graph, results_text = \
    validate(data_graph,
      shacl_graph=shacl_graph,
      inference='both',
      abort_on_first=False,
      allow_infos=False,
      allow_warnings=False,
      meta_shacl=False,
      advanced=False,
      js=False,
      debug=False)

# for (subject, predicate, object) in results_graph:
#     print(subject, predicate, object)

with open('validation_results.txt', 'w') as results_file:
  results_file.write(results_text)

results_graph.serialize('validation_results.ttl')

