import collections

from rdflib import Graph, RDF, OWL, URIRef, RDFS, SKOS, BNode


def analyse_definitions_in_ontology(ontology: Graph) -> dict:
    definition_analysis = dict()
    owl_classes = set(ontology.subjects(predicate=RDF.type, object=OWL.Class))
    for owl_class in owl_classes:
        owl_class_definitional_consistency = __get_owl_class_definitional_consistency(owl_class=owl_class, ontology=ontology)
        definition_analysis[owl_class] = owl_class_definitional_consistency
    ordered_definition_analysis = collections.OrderedDict(sorted(definition_analysis.items(), key=lambda da: da[1]))
    print(ordered_definition_analysis)
    return ordered_definition_analysis
    
    
def __get_owl_class_definitional_consistency(owl_class: URIRef, ontology: Graph) -> float:
    s=owl_class.defrag()
    owl_class_definitional_consistency = 0.0
    owl_class_label = ontology.label(subject=owl_class)
    owl_class_definitions = list(ontology.objects(subject=owl_class, predicate=SKOS.definition))
    if len(owl_class_definitions) == 0:
        return 0.0
    owl_class_definition = ' '.join(owl_class_definitions)
    owl_class_superclasses = set(ontology.objects(subject=owl_class, predicate=RDFS.subClassOf))
    for owl_class_superclass in owl_class_superclasses:
        if isinstance(owl_class_superclass, URIRef):
            owl_class_definition_overlap = \
                __get_owl_named_resource_definition_overlap(
                    definition=owl_class_definition,
                    named_resource=owl_class_superclass,
                    ontology=ontology)
        else:
            owl_class_definition_overlap = \
                __get_owl_bnode_definition_overlap(
                    definition=owl_class_definition,
                    bnode=owl_class_superclass,
                    ontology=ontology)
        owl_class_definitional_consistency += owl_class_definition_overlap
            
    return owl_class_definitional_consistency
    
    
def __get_owl_named_resource_definition_overlap(definition: str, named_resource: URIRef, ontology: Graph) -> float:
    named_resource_label = ontology.label(subject=named_resource)
    if named_resource_label in definition:
        return len(named_resource_label.replace(' ', ''))/len(definition.replace(' ', ''))
    else:
        return 0.0
    
    
def __get_owl_bnode_definition_overlap(definition: str, bnode: BNode, ontology: Graph) -> float:
    owl_bnode_definition_overlap = 0.0
    bnode_types = set(ontology.objects(subject=bnode, predicate=RDF.type))
    if OWL.Restriction in bnode_types:
        owl_bnode_definition_overlap = \
            __get_owl_restriction_definition_overlap(
                definition=definition,
                owl_restriction=bnode,
                ontology=ontology)
    return owl_bnode_definition_overlap


def __get_owl_restriction_definition_overlap(definition: str, owl_restriction: BNode, ontology: Graph) -> float:
    someValuesFrom_restricting_classes = set(ontology.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    allValuesFrom_restricting_classes = set(ontology.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    onClass_restricting_classes = set(ontology.objects(subject=owl_restriction, predicate=OWL.onClass))
    restricting_classes = someValuesFrom_restricting_classes.union(allValuesFrom_restricting_classes.union(onClass_restricting_classes))
    owl_restriction_definition_overlap = 0.0
    for restricting_class in restricting_classes:
        if isinstance(restricting_class, URIRef):
            owl_restricting_class_definition_overlap = \
                __get_owl_named_resource_definition_overlap(
                    definition=definition,
                    named_resource=restricting_class,
                    ontology=ontology)
        else:
            owl_restricting_class_definition_overlap = \
                __get_owl_bnode_definition_overlap(
                    definition=definition,
                    bnode=restricting_class,
                    ontology=ontology)
        owl_restriction_definition_overlap += owl_restricting_class_definition_overlap
    properties = set(ontology.objects(subject=owl_restriction, predicate=OWL.onProperty))
    owl_restricting_properties_definition_overlap = 0.0
    for property in properties:
        if isinstance(property, URIRef):
            owl_restricting_property_definition_overlap = \
                __get_owl_named_resource_definition_overlap(
                    definition=definition,
                    named_resource=property,
                    ontology=ontology)
            owl_restricting_properties_definition_overlap += owl_restricting_property_definition_overlap

    owl_restriction_definition_overlap += owl_restricting_properties_definition_overlap
    
    return owl_restriction_definition_overlap
    

fibo = Graph()
fibo.parse(r'/Users/pawel.garbacz/Documents/edmc/python/projects/edmc_tools/resources/dev.fibo-quickstart.ttl')
definition_analysis = analyse_definitions_in_ontology(ontology=fibo)
for owl_class, overlap in definition_analysis.items():
    if overlap == 0:
        fibo = fibo.remove((owl_class, None, None))
        fibo = fibo.remove((None, None, owl_class))
fibo.serialize(r'/Users/pawel.garbacz/Documents/edmc/python/projects/edmc_tools/resources/dev.fibo-quickstart_satori.ttl')
fibo.close()