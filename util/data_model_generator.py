import networkx
from owlready2 import *
from tqdm import tqdm

loopy_classes = []

onto = get_ontology('file:////Users/pawel.garbacz/idmp/AboutIDMPDevMerged.rdf').load()

def len_list(l):
    return len(l)


def collect_neighbours(ont_class_to_add, ont_class_to_search, graph: networkx.DiGraph) -> networkx.DiGraph:
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
                if restricted_resource is None:
                    restricted_resource = 'str'
                new_graph = graph.copy()
                if isinstance(restricted_resource, LogicalClassConstruct):
                    for logical_class in restricted_resource.Classes:
                        if isinstance(restricted_resource, Or):
                            new_graph.add_edge(ont_class_to_add, logical_class, label=restricting_property)
                        if isinstance(restricted_resource, And):
                            new_graph.add_edge(ont_class_to_add, logical_class, label=restricting_property)
                        new_graph = collect_neighbours(logical_class, logical_class, new_graph)
                new_graph.add_edge(ont_class_to_add, restricted_resource, label=restricting_property)
                if len(list(graph.edges)) == len(list(new_graph.edges)):
                    loopy_classes.append(ont_class_to_add)
                    continue
                else:
                    graph = new_graph
                    
                if isinstance(restricted_resource, ThingClass):
                    graph = collect_neighbours(restricted_resource, restricted_resource, graph)
                # else:
                #     return graph
            
        else:
            # graph.add_edge(ont_class_to_add, ont_class_superclass, label=rdfs_subclassof)
            graph = collect_neighbours(ont_class_to_add, ont_class_superclass, graph)

    return graph



ont_classes = onto.search(iri='https://spec.pistoiaalliance.org/idmp/ontology/ISO/ISO11238-Substances/Substance')
ont_class = ont_classes[0]
graph = collect_neighbours(ont_class, ont_class, networkx.DiGraph())
networkx.write_edgelist(G=graph,path='graph.txt',delimiter='|')
# paths = list(networkx.all_simple_paths(graph, source=ont_class, target=str))
# paths = list(networkx.simple_path(graph, source=ont_class).values())
paths = list()
for node in list(graph.nodes):
    paths += list(networkx.all_simple_paths(graph, source=ont_class, target=node))
# paths = list(networkx.all_simple_paths(graph, source=ont_class, target=list(graph.nodes)[1]))
paths.sort(key=len_list, reverse=False)
subclasses_map = dict()
subproperties_map = dict()
extended_paths = list()
for path in paths:
    extended_path = list()
    for i in range(0, len(path)-1):
        source = path[i]
        sink = path[i+1]
        edge_dict = graph.edges[source, sink]
        edge=edge_dict['label']
        triple = [source, edge, sink]
        if i == 0:
            extended_path.append(source)
        extended_path.append(edge)
        extended_path.append(sink)
        if source not in subclasses_map:
            subclasses_map[source] = list(onto.search(subclass_of=source))
        if edge not in subproperties_map:
            subproperties_map[edge] = list(onto.search(subproperty_of=edge))
        if isinstance(sink, ThingClass):
            if sink not in subclasses_map:
                subclasses_map[sink] = list(onto.search(subclass_of=sink))
    extended_paths.append(extended_path)
    
short_paths = list()
for path in extended_paths:
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

redundant_paths = list()
for i in range(len(short_paths)):
    path1 = short_paths[i]
    if Thing in path1:
        redundant_paths.append(path1)
    for j in range(i+1, len(short_paths)):
        path2 = short_paths[j]
        if path1 == path2:
            redundant_paths.append(path2)
        if all(elem in path1 for elem in path2):
            redundant_paths.append(path2)
        if all(elem in path2 for elem in path1):
            redundant_paths.append(path1)

print(len(extended_paths))
print(len(short_paths))
print(len(redundant_paths))

paths_file = open('paths.txt', 'w')
for path in short_paths:
    if path not in redundant_paths:
        paths_file.write(str(path)+'\n')
paths_file.close()
