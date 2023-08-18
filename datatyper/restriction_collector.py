import logging

from rdflib import Graph, RDF, OWL, RDFS, BNode, URIRef


def collect_model_relevant_owl_restrictions(ontology: Graph):
    datatypes_attributes_protomap = __collect_owl_restrictions(ontology=ontology)
    sparse_datatypes_attributes_map = __filter_out_inherited_restrictions(datatypes_attributes_map=datatypes_attributes_protomap, ontology=ontology)
    non_circular_datatypes_attributes_map = __filter_out_circular_restrictions(datatypes_attributes_map=sparse_datatypes_attributes_map)
    return non_circular_datatypes_attributes_map

def __collect_owl_restrictions(ontology: Graph) -> dict:
    logging.info(msg='Collecting all restrictions')
    datatypes_attributes_protomap = dict()
    owl_restrictions = ontology.subjects(predicate=RDF.type, object=OWL.Restriction)
    for owl_restriction in owl_restrictions:
        restricted_classes = ontology.transitive_subjects(predicate=RDFS.subClassOf, object=owl_restriction)
        for restricted_class in restricted_classes:
            if isinstance(restricted_class, URIRef):
                restricting_class, restricting_property = \
                    __get_restricting_class_and_property_for_owl_restriction(
                        owl_restriction=owl_restriction,
                        ontology=ontology)
                if not restricting_class or not restricting_property:
                    continue
                if restricted_class in datatypes_attributes_protomap:
                    restrictions = datatypes_attributes_protomap[restricted_class]
                else:
                    restrictions = set()
                    datatypes_attributes_protomap[restricted_class] = restrictions
                restrictions.add((restricting_property, restricting_class))
            
    return datatypes_attributes_protomap
            
            
def __get_restricting_class_and_property_for_owl_restriction(owl_restriction: BNode, ontology: Graph) -> tuple:
    restricting_property = list(ontology.objects(subject=owl_restriction, predicate=OWL.onProperty))[0]
    someValuesFrom_restricting_classes = list(ontology.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    if len(someValuesFrom_restricting_classes) == 1:
        someValuesFrom_restricting_class = someValuesFrom_restricting_classes[0]
        if isinstance(someValuesFrom_restricting_class, URIRef):
            return someValuesFrom_restricting_class, restricting_property
    
    allValuesFrom_restricting_classes = list(ontology.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    if len(allValuesFrom_restricting_classes) == 1:
        allValuesFrom_restricting_class = allValuesFrom_restricting_classes[0]
        if isinstance(allValuesFrom_restricting_class, URIRef):
            return allValuesFrom_restricting_class, restricting_property
    
    onClass_restricting_classes = list(ontology.objects(subject=owl_restriction, predicate=OWL.onClass))
    if len(onClass_restricting_classes) == 1:
        onClass_restricting_class = onClass_restricting_classes[0]
        if isinstance(onClass_restricting_class, URIRef):
            return onClass_restricting_class, restricting_property
        
    return None, None


def __filter_out_inherited_restrictions(datatypes_attributes_map: dict, ontology: Graph) -> dict:
    logging.info(msg='Filtering out inherited restrictions')
    sparse_datatypes_attributes_map = dict()
    for restricted_class, restrictions in datatypes_attributes_map.items():
        sparse_restrictions = restrictions.copy()
        for restriction1 in restrictions:
            for restriction2 in restrictions:
                if restriction1 == restriction2:
                    continue
                if __restriction2_is_inheritable_from_restriction_1(restriction1=restriction1, restriction2=restriction2, ontology=ontology):
                    if restriction2 in sparse_restrictions:
                        sparse_restrictions.remove(restriction2)
        sparse_datatypes_attributes_map[restricted_class] = sparse_restrictions
    return sparse_datatypes_attributes_map
    
def __restriction2_is_inheritable_from_restriction_1(restriction1: list, restriction2: list, ontology: Graph) -> bool:
    restricting_property1 = restriction1[0]
    restricting_class1 = restriction1[1]
    restricting_property2 = restriction2[0]
    restricting_class2 = restriction2[1]
    if restricting_property2 in set(ontology.transitive_objects(subject=restricting_property1,predicate=RDFS.subPropertyOf)):
        if restricting_class2 in set(ontology.transitive_objects(subject=restricting_class1, predicate=RDFS.subClassOf)):
            return True
        if restricting_class2 == OWL.Thing:
            return True
    return False


def __filter_out_circular_restrictions(datatypes_attributes_map: dict) -> dict:
    logging.info(msg='Filtering our circular restrictions')
    non_circular_datatypes_attributes_map = dict()
    for restricted_class, restrictions in datatypes_attributes_map.items():
        non_cirular_restrictions = restrictions.copy()
        for restriction in restrictions:
            if __is_restriction_cirular(restriction=restriction, datatypes_attributes_map=datatypes_attributes_map, visited_classes=set()):
                if restriction in non_cirular_restrictions:
                    non_cirular_restrictions.remove(restriction)
                    # logging.info(msg='Dropping' + str(restriction))
        non_circular_datatypes_attributes_map[restricted_class] = non_cirular_restrictions
    return non_circular_datatypes_attributes_map
    
    
def __is_restriction_cirular(restriction: tuple, datatypes_attributes_map: dict, visited_classes: set) -> bool:
    restricting_class = restriction[1]
    if restricting_class in visited_classes:
        return True
    visited_classes.add(restricting_class)
    if restricting_class in datatypes_attributes_map:
        second_order_restrictions = datatypes_attributes_map[restricting_class]
        for second_order_restriction in second_order_restrictions:
            second_order_restricting_class = second_order_restriction[1]
            if second_order_restricting_class in visited_classes:
                return True
            second_order_restriction_is_circular = __is_restriction_cirular(restriction=second_order_restriction, datatypes_attributes_map=datatypes_attributes_map, visited_classes=visited_classes)
            if second_order_restriction_is_circular:
                return True
    return False
    
    
            