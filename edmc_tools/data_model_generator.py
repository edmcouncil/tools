import networkx
from owlready2 import *
from tqdm import tqdm

loopy_classes = []

onto = get_ontology(r'/Users/pawel.garbacz/Documents/makolab/honu/makolab/FinancialInstrumentsMerged.rdf').load()

def len_list(l):
    return len(l)


def collect_neighours(ont_class_to_add, ont_class_to_search, graph: networkx.DiGraph) -> networkx.DiGraph:
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
                new_graph.add_edge(ont_class_to_add, restricted_resource, label=restricting_property)
                if len(list(graph.edges)) == len(list(new_graph.edges)):
                    loopy_classes.append(ont_class_to_add)
                    continue
                else:
                    graph = new_graph
                    
                if isinstance(restricted_resource, ThingClass):
                    graph = collect_neighours(restricted_resource, restricted_resource, graph)
                else:
                    return graph
            
        else:
            # graph.add_edge(ont_class_to_add, ont_class_superclass, label=rdfs_subclassof)
            graph = collect_neighours(ont_class_to_add, ont_class_superclass, graph)

    return graph



ont_classes = onto.search(iri='https://www.honu.ai/ontologies/fibo/FinancialInstruments/Loan')
ont_class = ont_classes[0]
graph = collect_neighours(ont_class, ont_class, networkx.DiGraph())
networkx.write_edgelist(G=graph,path='graph.txt',delimiter='|')
paths = list(networkx.all_simple_paths(graph, source=ont_class, target=str))
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
redundant_paths = list()

for i in tqdm(range(0, len(extended_paths)-1)):
    extended_path_1 = extended_paths[i]
    if extended_path_1 in redundant_paths:
        continue
    for j in range(i+1, len(extended_paths)-2):
        extended_path_2 = extended_paths[j]
        if extended_path_2 in redundant_paths:
            continue
        drop_2 = False
        scope = len(extended_path_1)
        for k in range(0, scope-2, 2):
            triple_1 = [extended_path_1[k], extended_path_1[k+1], extended_path_1[k+2]]
            triple_2 = [extended_path_2[k], extended_path_2[k+1], extended_path_2[k+2]]
            if not triple_1 == triple_2:
                if triple_1[0] in subclasses_map[triple_2[0]] and triple_1[1] in subproperties_map[triple_2[1]]:
                    if isinstance(triple_1[2], ThingClass) and isinstance(triple_2[2], ThingClass):
                        if triple_1[2] in subclasses_map[triple_2[2]]:
                            drop_2 = True
                            break
                break
        if drop_2:
            if extended_path_2 not in redundant_paths:
                redundant_paths.append(extended_path_2)
        
# redundant_paths = list(set(tuple(path) for path in redundant_paths))
# print(redundant_paths)
print(len(redundant_paths))
print(len(extended_paths))
# print(relevant_extended_paths)
# print('***')
paths_file = open('paths.txt', 'w')
for path in extended_paths:
    if path not in redundant_paths:
        paths_file.write(str(path)+'\n')
paths_file.close()
