from pyshacl import validate
from rdflib import Graph

data_graph = Graph().parse('../resources/idmp_current/dev.idmp-quickstart.ttl')
shacl_graph = Graph().parse('../resources/idmp_current/dev.idmp-quickstart.shacl')


conforms, results_graph, results_text = \
    validate(data_graph,
      shacl_graph=shacl_graph,
      inference='rdfs',
      abort_on_first=False,
      allow_infos=False,
      allow_warnings=False,
      meta_shacl=False,
      advanced=False,
      js=False,
      debug=False)

# for (subject, predicate, object) in results_graph:
#     print(subject, predicate, object)

print(results_text)