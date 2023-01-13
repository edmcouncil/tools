import csv

from rdflib import Graph, URIRef, RDF, OWL, RDFS


def get_local_name(iri: URIRef, sep='/') -> str:
    if not '#' in iri:
        fragments = iri.split(sep=sep)
        local_name = fragments[-1]
    else:
        local_name = iri.fragment
    return local_name

graph = Graph()
graph.parse('TransportDevices.rdf')
nodes = list()
edges = list()
resources = set()

for (subject, predicate, object) in graph:
    if not isinstance(subject, URIRef) or not isinstance(predicate, URIRef) or not isinstance(object, URIRef):
        continue
    # if not 'edmcouncil' in str(subject) or not 'edmcouncil' in str(predicate) or not 'edmcouncil' in str(object):
    #     continue
    if not 'edmcouncil' in str(subject):
        continue
    subject_node = get_local_name(subject)
    predicate_node = get_local_name(predicate)
    object_node = get_local_name(object)
    if subject not in resources:
        nodes.append([subject_node])
        resources.add(subject)
    # if predicate not in resources:
    #     nodes.append([predicate_node])
    #     resources.add(predicate)
    if object not in resources:
        nodes.append([object_node])
        resources.add(object)
    edges.append([subject_node, object_node, predicate_node])
    
    
owl_restrictions = graph.subjects(predicate=RDF.type, object=OWL.Restriction)
for owl_restriction in owl_restrictions:
    restricted_classes = list(graph.subjects(object=owl_restriction, predicate=RDFS.subClassOf))
    restricted_class = restricted_classes[0]
    on_properties = list(graph.objects(subject=owl_restriction, predicate=OWL.onProperty))
    on_property = on_properties[0]
    restricting_classes_someValues = list(graph.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    restricting_classes_onClass = list(graph.objects(subject=owl_restriction, predicate=OWL.onClass))
    restricting_classes = restricting_classes_someValues + restricting_classes_onClass
    restricting_class = restricting_classes[0]
    restricted_class_node = get_local_name(restricted_class)
    restricting_class_node = get_local_name(restricting_class)
    restricting_property_node = get_local_name(on_property)
    edges.append([restricted_class_node, restricting_class_node, restricting_property_node])
    

with open('kumu_nodes.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    for node in nodes:
        writer.writerow(node)
    f.close()

with open('kumu_edges.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerows(edges)
    f.close()


    