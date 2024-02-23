import collections

import networkx
from owlready2 import *
from networkx import Graph
from xlsxwriter import Workbook

loopy_classes = []
type_map = {str: 'xsd.string', normstr: 'xsd:anyURI', bool: 'xsd:boolean', float: 'xsd:float'}


def list_length(l: list):
    return len(l)


def __collect_neighbours(ont_class_to_add, ont_class_to_search, graph: networkx.DiGraph) -> networkx.DiGraph:
    if ont_class_to_add in loopy_classes:
        return graph
    ont_class_superclasses = ont_class_to_search.is_a
    for ont_class_superclass in ont_class_superclasses:
        if ont_class_superclass in loopy_classes:
            continue
        if isinstance(ont_class_superclass, Restriction):
            restricting_property = ont_class_superclass.property
            restricted_resource = ont_class_superclass.value
            if restricting_property.some(restricted_resource) == ont_class_superclass or \
                    restricting_property.min(1, restricted_resource) == ont_class_superclass or \
                    restricting_property.exactly(1, restricted_resource) == ont_class_superclass:
                if restricted_resource in type_map:
                    restricted_resource = type_map[restricted_resource]
                new_graph = graph.copy()
                if isinstance(restricted_resource, LogicalClassConstruct):
                    for logical_class in restricted_resource.Classes:
                        if isinstance(restricted_resource, Or):
                            new_graph.add_edge(ont_class_to_add, logical_class, label=restricting_property)
                        if isinstance(restricted_resource, And):
                            new_graph.add_edge(ont_class_to_add, logical_class, label=restricting_property)
                        new_graph = __collect_neighbours(logical_class, logical_class, new_graph)
                new_graph.add_edge(ont_class_to_add, restricted_resource, label=restricting_property)
                if len(list(graph.edges)) == len(list(new_graph.edges)):
                    loopy_classes.append(ont_class_to_add)
                    continue
                else:
                    graph = new_graph
                    
                if isinstance(restricted_resource, ThingClass):
                    graph = __collect_neighbours(restricted_resource, restricted_resource, graph)
        else:
            graph = __collect_neighbours(ont_class_to_add, ont_class_superclass, graph)

    return graph


def __remove_inferrable_edges(graph: Graph) -> Graph:
    pruned_graph = graph.copy()
    for edge1 in graph.edges:
        source1 = edge1[0]
        sink1 = edge1[1]
        edge_dict1 = graph.edges[source1, sink1]
        edge_type1 = edge_dict1['label']
        for edge2 in graph.edges:
            source2 = edge2[0]
            sink2 = edge2[1]
            edge_dict2 = graph.edges[source2, sink2]
            edge_type2 = edge_dict2['label']
            if not edge1 == edge2:
                if source1 == source2 or source2 in source1.is_a:
                    if edge_type1 == edge_type2 or edge_type2 in edge_type1.is_a:
                        if sink1 == sink2 or sink2 in sink1.is_a:
                            if edge2 in pruned_graph.edges:
                                pruned_graph.remove_edge(source2, sink2)
    return pruned_graph


def __get_paths_from_graph(graph: Graph, ont_class) -> list:
    paths = list()
    for node in list(graph.nodes):
        paths += list(networkx.all_simple_paths(graph, source=ont_class, target=node))
    paths.sort(key=list_length, reverse=False)
    return paths
    
    
def __extend_paths(paths: list, ontology: Ontology, graph: Graph) -> list:
    subclasses_map = dict()
    subproperties_map = dict()
    extended_paths = list()
    for path in paths:
        extended_path = list()
        for i in range(0, len(path)-1):
            source = path[i]
            sink = path[i+1]
            edge_dict = graph.edges[source, sink]
            edge = edge_dict['label']
            if i == 0:
                extended_path.append(source)
            extended_path.append(edge)
            extended_path.append(sink)
            if source not in subclasses_map:
                subclasses_map[source] = list(ontology.search(subclass_of=source))
            if edge not in subproperties_map:
                subproperties_map[edge] = list(ontology.search(subproperty_of=edge))
            if isinstance(sink, ThingClass):
                if sink not in subclasses_map:
                    subclasses_map[sink] = list(ontology.search(subclass_of=sink))
        extended_paths.append(extended_path)
    return extended_paths


def __shorten_paths(paths: list) -> list:
    short_paths = list()
    for path in paths:
        path_cutoff = -1
        for i in range(len(path)):
            try:
                inverse = path[i].inverse_property
            except:
                inverse = None
            for j in range(i + 1, len(path)):
                if path[j] == inverse:
                    path_cutoff = j
                    break
            if path_cutoff > -1:
                break
        if path_cutoff > -1:
            path = path[0:path_cutoff]
        short_paths.append(path)
    return short_paths


def __removed_redundant_paths(paths: list) -> list:
    redundant_path_indices = set()
    for i in range(len(paths)):
        path1 = paths[i]
        if Thing in path1:
            redundant_path_indices.add(i)
        for j in range(i + 1, len(paths)):
            path2 = paths[j]
            if path1 == path2:
                redundant_path_indices.add(j)
            elif str(path2)[1:-1] in str(path1)[1:-1]:
                redundant_path_indices.add(j)
            elif str(path1)[1:-1] in str(path2)[1:-1]:
                redundant_path_indices.add(i)
    redundant_paths = list()
    for index in range(len(paths)):
        if index not in redundant_path_indices:
            redundant_paths.append(paths[index])
    return redundant_paths
    
    
def prune_paths(paths: list, redundant_paths: list) -> list:
    pruned_paths = list()
    for path in paths:
        if path not in redundant_paths and '|' not in str(path):
            pruned_paths.append(path)
    return pruned_paths


def __get_node_typed_triples(paths: list) -> dict:
    node_typed_triples = dict()
    type_nodes = set()
    for path in paths:
        for node_index in range(len(path)):
            if (node_index % 2) == 0:
                type_nodes.add(path[node_index])
    type_nodes = list(type_nodes)
    for node_type in type_nodes:
        node_type_string = str(node_type).split('.')[-1]
        for path in paths:
            for node_index in range(len(path)):
                node = path[node_index]
                if node_index > len(path)-3:
                    continue
                if node == node_type:
                    if node_type_string in node_typed_triples:
                        typed_triples = node_typed_triples[node_type_string]
                    else:
                        typed_triples = list()
                        node_typed_triples[node_type_string] = typed_triples
                    node_string = str(node)
                    next_node_string = str(path[node_index + 1])
                    next_next_node_string = str(path[node_index + 2])
                    if [node_string, next_node_string, next_next_node_string] not in typed_triples:
                        typed_triples.append([node_string, next_node_string, next_next_node_string])
    node_typed_triples = collections.OrderedDict(sorted(node_typed_triples.items()))
    return node_typed_triples


def __add_paths_to_worksheet_in_workbook(paths: list, worksheet_name: str, workbook: Workbook, order_paths: bool):
    if order_paths:
        paths.sort()
    worksheet = workbook.add_worksheet(worksheet_name[:30])
    for path_index in range(len(paths)):
        path = paths[path_index]
        for node_index in range(len(path)):
            node = path[node_index]
            worksheet.write(path_index, node_index, str(node))


def __save_paths_to_excel(paths: list, excel_file_path: str):
    workbook = Workbook(excel_file_path)
    __add_paths_to_worksheet_in_workbook(paths=paths, worksheet_name='raw', workbook=workbook, order_paths=False)
    node_typed_triples = __get_node_typed_triples(paths=paths)
    for node_type, typed_triples in node_typed_triples.items():
        worksheet_name = str(node_type).split('.')[-1]
        __add_paths_to_worksheet_in_workbook(paths=typed_triples, worksheet_name=worksheet_name, workbook=workbook, order_paths=True)
    workbook.close()


def generate_model_for_class(ontology_file_path: str, ont_class_iri: str):
    ontology = get_ontology(ontology_file_path).load()
    ont_classes = ontology.search(iri=ont_class_iri)
    ont_class = ont_classes[0]
    graph = __collect_neighbours(ont_class, ont_class, networkx.DiGraph())
    pruned_graph = __remove_inferrable_edges(graph=graph)
    paths = __get_paths_from_graph(graph=pruned_graph, ont_class=ont_class)
    extended_paths = __extend_paths(paths=paths, ontology=ontology, graph=pruned_graph)
    short_paths = __shorten_paths(paths=extended_paths)
    pruned_paths = __removed_redundant_paths(paths=short_paths)
    ont_class_local_name = ont_class_iri.split(sep='/')[-1]
    __save_paths_to_excel(paths=pruned_paths, excel_file_path=ont_class_local_name + '.xlsx')
    
    
generate_model_for_class(
    ontology_file_path='file:////Users/pawel.garbacz/idmp/AboutIDMPDevMerged.rdf',
    ont_class_iri='https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11615-MedicinalProducts/PackageItem')
