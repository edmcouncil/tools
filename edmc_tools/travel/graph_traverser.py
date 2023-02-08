import csv
import json

from rdflib import Graph as SemanticGraph, RDF, URIRef, OWL, BNode, RDFS
from networkx.readwrite import json_graph
from networkx import Graph, DiGraph
from rdflib.term import Node, Literal
import networkx
import matplotlib.pyplot as plt

from shacl.data_model_generator import generate_shacl_model_from_ontology
from shacl.objects.shacl_model_cardinality_restriction import ShaclModelCardinalityRestriction
from shacl.objects.shacl_model_identified_class import ShaclModelIdentifiedClass

ignored_edges = [RDF.type]
edge_property_attribute = 'edge labels'


def traverse_graph_from(source_node_iri: URIRef, graph: DiGraph):
    shacl_class = ShaclModelIdentifiedClass.get_shacl_identified_class_from_owl(owl_class=source_node_iri)
    for attribute in shacl_class.attributes:
        if not isinstance(attribute, ShaclModelCardinalityRestriction):
            continue
        if attribute.cardinality.min < 1:
            continue
        edge = attribute.property.iri
        sink_node = attribute.range.iri
        if sink_node == Literal:
            sink_node = RDFS.Literal
        if edge in ignored_edges:
            continue
        
        # edge_attributes = graph.get_edge_data(u=source_node_iri, v=sink_node)
        # if not edge_attributes == None:
        #     if edge_property_attribute in edge_attributes:
        #         edge_labels = edge_attributes[edge_property_attribute]
        #     else:
        #         edge_labels = set()
        # else:
        #     edge_labels = set()
        
        source = str(source_node_iri).split('/')[-1]
        sink = str(sink_node).split('/')[-1]
        edge_label = str(edge).split('/')[-1]
        min_cardinality = attribute.cardinality.min
        max_cardinality = attribute.cardinality.max
        edge_labels = [edge_label, 'min='+str(min_cardinality)]
        if max_cardinality > -1:
            edge_labels.append('max='+str(max_cardinality))

        
        if source == sink:
            continue

        if sink in graph.nodes:
            sink_ancestors = networkx.algorithms.ancestors(graph, sink)
            if source in sink_ancestors:
                if [source, sink] in graph.edges:
                    continue
        edge_label = ' '.join(edge_labels)
        graph.add_edge(u_of_edge=source, v_of_edge=sink,attr=edge_label)
        
        if not (edge, RDF.type, OWL.DatatypeProperty) in semantic_graph:
            traverse_graph_from(source_node_iri=sink_node, graph=graph)
                    

def pathify(edges: list, paths: list, start_node: str) -> list:
    if len(paths) == 0:
        paths.append(start_node)
    continue_pathify = True
    while (continue_pathify):
        continue_pathify = False
        for path in paths.copy():
            edges_copy = edges.copy()
            for edge in edges_copy:
                removed = False
                if edge_can_be_added_to_paths(edge=edge, paths=paths):
                    if path[0] == edge[1]:
                        if edge[0] == start_node:
                            if path in paths:
                                paths.remove(path)
                            extended_path = [edge[0]] + [edge[1]] + path
                            paths.append(extended_path)
                            paths.append(extended_path)
                            removed = True
                    if path[-1] == edge[0]:
                        if path in paths:
                            paths.remove(path)
                        extended_path = path + [edge[1]] + [edge[2]]
                        paths.append(extended_path)
                        removed = True
                if removed:
                    edges.remove(edge)
                    continue_pathify = True
                else:
                    if edge[0] == start_node:
                        if list(edge) not in paths:
                            paths.append(list(edge))
                            edges.remove(edge)
                            continue_pathify = True
    return paths
                

def edge_can_be_added_to_paths(edge: list, paths: list) -> bool:
    for path in paths:
        if all(i in path for i in edge):
            return False
    return True


semantic_graph = SemanticGraph()
semantic_graph.parse('resources/idmp_current/dev.idmp-quickstart.ttl')
generate_shacl_model_from_ontology(ontology=semantic_graph)
graph = DiGraph()
traverse_graph_from(
    source_node_iri=URIRef('https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/Substance'),
    graph=graph)

# print(graph.nodes)
# print('***')
# print(graph.edges.data('attr'))

# nodes = list()
# for node in graph.nodes:
#     nodes.append([str(node)])
#
# with open("nodes.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerows(nodes)
#     f.close()
#
# with open("edges.csv", "w") as f:
#     writer = csv.writer(f)
#     writer.writerows(graph.edges.data('attr'))
#     f.close()

triple_edges = list()
for edge in graph.edges.data('attr'):
    triple_edges.append([edge[0], edge[2], edge[1]])

paths = pathify(edges=triple_edges,paths=[], start_node='Substance')

with open("paths.csv", "w") as f:
    writer = csv.writer(f)
    writer.writerows(paths)
    f.close()
            
        


