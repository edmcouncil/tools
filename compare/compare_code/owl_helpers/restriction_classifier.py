import sys

from rdflib import URIRef, BNode, Graph, OWL


def get_restricting_property(restriction: BNode, ontology: Graph) -> URIRef:
    restricting_properties = list(ontology.objects(subject=restriction, predicate=OWL.onProperty))
    restricting_property = restricting_properties[0]
    return restricting_property


def get_restricting_type_and_class(restriction: BNode, ontology: Graph) -> tuple:
    restricting_classes = list(ontology.objects(subject=restriction, predicate=OWL.onClass))
    restricting_datatypes = list(ontology.objects(subject=restriction, predicate=OWL.onDataRange))
    restricting_classes_some_values = list(ontology.objects(subject=restriction, predicate=OWL.someValuesFrom))
    restricting_classes_all_values = list(ontology.objects(subject=restriction, predicate=OWL.allValuesFrom))
    restricting_values = list(ontology.objects(subject=restriction, predicate=OWL.hasValue))
    
    if len(restricting_classes_some_values) == 1:
        return tuple([OWL.someValuesFrom, restricting_classes_some_values[0]])
    if len(restricting_classes_all_values) == 1:
        return tuple([OWL.allValuesFrom, restricting_classes_all_values[0]])
    if len(restricting_classes) == 1:
        return tuple([OWL.onClass, restricting_classes[0]])
    if len(restricting_datatypes) == 1:
        return tuple([OWL.onDataRange, restricting_datatypes[0]])
    if len(restricting_values) == 1:
        return tuple([OWL.hasValue, restricting_values[0]])
    return tuple([None, None])
    
    
def get_restriction_modality_and_cardinality_value(restriction: BNode, ontology: Graph) -> tuple:
    restricting_cardinality_min = list(ontology.objects(subject=restriction, predicate=OWL.minCardinality))
    restricting_qualified_cardinality_min = list(ontology.objects(subject=restriction, predicate=OWL.minQualifiedCardinality))
    restricting_cardinality_max = list(ontology.objects(subject=restriction, predicate=OWL.maxCardinality))
    restricting_qualified_cardinality_max = list(ontology.objects(subject=restriction, predicate=OWL.maxQualifiedCardinality))
    restricting_cardinality = list(ontology.objects(subject=restriction, predicate=OWL.cardinality))
    restricting_qualified_cardinality = list(ontology.objects(subject=restriction, predicate=OWL.qualifiedCardinality))
    restricting_classes_some_values = list(ontology.objects(subject=restriction, predicate=OWL.someValuesFrom))
    restricting_classes_all_values = list(ontology.objects(subject=restriction, predicate=OWL.allValuesFrom))
    restricting_values = list(ontology.objects(subject=restriction, predicate=OWL.hasValue))
    restricting_datatypes = list(ontology.objects(subject=restriction, predicate=OWL.onDataRange))
    restricting_hasSelf = list(ontology.objects(subject=restriction, predicate=OWL.hasSelf))
    
    if len(restricting_cardinality_min) == 1:
        return tuple([OWL.minCardinality, restricting_cardinality_min[0]])
    if len(restricting_qualified_cardinality_min) == 1:
        return tuple([OWL.minQualifiedCardinality, restricting_qualified_cardinality_min[0]])
    if len(restricting_cardinality_max) == 1:
        return tuple([OWL.maxCardinality, restricting_cardinality_max[0]])
    if len(restricting_qualified_cardinality_max) == 1:
        return tuple([OWL.maxQualifiedCardinality, restricting_qualified_cardinality_max[0]])
    if len(restricting_cardinality) == 1:
        return tuple([OWL.cardinality, restricting_cardinality[0]])
    if len(restricting_classes_some_values) == 1:
        return tuple([OWL.cardinality, 1])
    if len(restricting_classes_all_values) == 1:
        return tuple([OWL.cardinality, -1])
    if len(restricting_values) == 1:
        return tuple([OWL.cardinality, 1])
    if len(restricting_datatypes) == 1:
        return tuple([OWL.cardinality, 1])
    if len(restricting_qualified_cardinality) == 1:
        return tuple([OWL.qualifiedCardinality, restricting_qualified_cardinality[0]])
    if len(restricting_hasSelf) == 1:
        return tuple([OWL.hasSelf, restricting_hasSelf[0]])
    sys.exit(-1)