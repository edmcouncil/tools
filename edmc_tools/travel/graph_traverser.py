import json

from rdflib import Graph as SemanticGraph, RDF, URIRef, OWL, BNode
from networkx.readwrite import json_graph
from networkx import Graph, DiGraph
from rdflib.term import Node
import networkx
import matplotlib.pyplot as plt

ignored_edges = [RDF.type]
edge_property_attribute = 'edge labels'


def traverse_graph_from(semantic_graph: SemanticGraph, source_node_iri: URIRef, graph: DiGraph):
    edges_and_sink_nodes = list(semantic_graph.predicate_objects(subject=source_node_iri))
    for edge_and_sink in edges_and_sink_nodes:
        edge = edge_and_sink[0]
        sink_node = edge_and_sink[1]
        if edge in ignored_edges:
            continue
        if not (sink_node, RDF.type, OWL.Restriction) in semantic_graph:
            continue
        
        owl_property, owl_restricted_class, cardinality, cardinality_type = \
            get_restricted_class_property_cardinality_from_owl_restriction(
                owl_restriction=sink_node,
                semantic_graph=semantic_graph)
        
        if owl_restricted_class == None:
            continue
        
        if (owl_restricted_class, RDF.type, OWL.Restriction) in semantic_graph:
            continue
        
        edge_attributes = graph.get_edge_data(u=source_node_iri, v=owl_restricted_class)
        if not edge_attributes == None:
            if edge_property_attribute in edge_attributes:
                edge_labels = edge_attributes[edge_property_attribute]
            else:
                edge_labels = set()
        else:
            edge_labels = set()
        
        source = str(source_node_iri).split('/')[-1]
        sink = str(owl_restricted_class).split('/')[-1]
        edge_label = str(owl_property).split('/')[-1]
        edge_labels.add(edge_label)
        
        if source == sink:
            continue

        if sink in graph.nodes:
            sink_ancestors = networkx.algorithms.ancestors(graph, sink)
            if source in sink_ancestors:
                continue
        
        graph.add_edge(u_of_edge=source, v_of_edge=sink,attr={edge_property_attribute: edge_labels})
        
        if not (owl_property, RDF.type, OWL.DatatypeProperty) in semantic_graph:
            traverse_graph_from(
                semantic_graph=semantic_graph,
                source_node_iri=owl_restricted_class, graph=graph)
                    


def get_restricted_class_property_cardinality_from_owl_restriction(owl_restriction: Node,semantic_graph: SemanticGraph) -> tuple:
    owl_properties = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.onProperty))
    owl_property = owl_properties[0]
    
    owl_ranges_someValuesFrom = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    owl_ranges_allValuesFrom = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    owl_ranges_qualifiedCardinality = list(
        semantic_graph.objects(subject=owl_restriction, predicate=OWL.qualifiedCardinality))
    owl_ranges_cardinality = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.cardinality))
    owl_ranges_minCardinality = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.minCardinality))
    owl_ranges_maxCardinality = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.maxCardinality))
    owl_ranges_qualifiedMinCardinality = list(
        semantic_graph.objects(subject=owl_restriction, predicate=OWL.minQualifiedCardinality))
    owl_ranges_qualifiedMaxCardinality = list(
        semantic_graph.objects(subject=owl_restriction, predicate=OWL.maxQualifiedCardinality))
    owl_onClass = list(semantic_graph.objects(subject=owl_restriction, predicate=OWL.onClass))
    
    owl_restricted_class = None
    cardinality = None
    cardinality_type = None
    
    if len(owl_onClass) == 1:
        owl_restricted_class = owl_onClass[0]
    
    if len(owl_ranges_someValuesFrom) == 1:
        owl_restricted_class = owl_ranges_someValuesFrom[0]
        cardinality = 1
        cardinality_type = OWL.someValuesFrom
    if len(owl_ranges_cardinality) == 1:
        owl_restricted_class = OWL.Thing
        cardinality = owl_ranges_cardinality[0]
        cardinality_type = OWL.cardinality
    if len(owl_ranges_qualifiedCardinality) == 1:
        owl_restricted_class = type(owl_ranges_qualifiedCardinality[0])
        cardinality = owl_ranges_qualifiedCardinality[0]
        cardinality_type = OWL.qualifiedCardinality
    if len(owl_ranges_minCardinality) == 1:
        owl_restricted_class = OWL.Thing
        cardinality = owl_ranges_minCardinality[0]
        cardinality_type = OWL.minCardinality
    if len(owl_ranges_maxCardinality) == 1:
        owl_restricted_class = OWL.Thing
        cardinality = owl_ranges_maxCardinality[0]
        cardinality_type = OWL.maxCardinality
    if len(owl_ranges_qualifiedMinCardinality) == 1:
        cardinality = owl_ranges_qualifiedMinCardinality[0]
        cardinality_type = OWL.minQualifiedCardinality
    if len(owl_ranges_qualifiedMaxCardinality) == 1:
        cardinality = owl_ranges_qualifiedMaxCardinality[0]
        cardinality_type = OWL.maxQualifiedCardinality
    
    return owl_property, owl_restricted_class, cardinality, cardinality_type


semantic_graph = SemanticGraph()
semantic_graph.parse('resources/idmp_current/dev.idmp-quickstart.ttl')
graph = DiGraph()
traverse_graph_from(
    semantic_graph=semantic_graph,
    source_node_iri=URIRef('https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/Substance'),
    graph=graph)
v=0
# networkx.write_gml(graph,'graph.gml')
# print(json.dumps(json_graph.node_link_data(graph), indent=4))
# networkx.draw_networkx(graph, pos=networkx.spectral_layout(graph))
# plt.savefig("graph.png")


