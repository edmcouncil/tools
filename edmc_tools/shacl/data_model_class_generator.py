from rdflib import Graph, OWL, URIRef, RDFS, RDF
from rdflib.term import Node, Literal, Identifier

from shacl.objects.shacl_model_cardinality import ShaclModelCardinality
from shacl.objects.shacl_model_cardinality_restriction import ShaclModelCardinalityRestriction
from shacl.objects.shacl_model_container_class import ShaclModelCollection
from shacl.objects.shacl_model_identified_class import ShaclModelIdentifiedClass
from shacl.objects.shacl_model_literal import ShaclModelLiteral
from shacl.objects.shacl_model_node import ShaclModelNode
from shacl.objects.shacl_model_property import ShaclModelProperty
from shacl.objects.shacl_model_value_attribute import ShaclModelValueRestriction
from shacl.objects.shacl_severity import ShaclSeverity
from shacl.resource_recognizer import if_resource_is_datatype


def generate_model_class_from_owl_class_with_attributes(owl_class: URIRef, ontology: Graph, is_datatype: bool) -> ShaclModelIdentifiedClass:
    shacl_model_class = generate_model_class_from_owl_class(owl_identifier=owl_class, is_datatype=is_datatype)
    owl_superclasses = list(ontology.objects(predicate=RDFS.subClassOf, subject=owl_class))
    for owl_superclass in owl_superclasses:
        shacl_model_node = process_owl_node_by_type(node=owl_superclass,ontology=ontology)
        if not isinstance(shacl_model_node, ShaclModelIdentifiedClass):
            shacl_model_class.attributes.add(shacl_model_node)
    return shacl_model_class


def generate_model_class_from_owl_class(owl_identifier: Identifier, is_datatype: bool) -> ShaclModelIdentifiedClass:
    if owl_identifier in ShaclModelIdentifiedClass.registry:
        return ShaclModelIdentifiedClass.registry[owl_identifier]
    shacl_model_class = ShaclModelIdentifiedClass(iri=owl_identifier, attributes=set(), super_classes=set(), is_datatype=is_datatype)
    return shacl_model_class

def generate_attribute_from_owl_restriction(owl_restriction: Node, ontology: Graph) -> ShaclModelNode:
    owl_properties = list(ontology.objects(subject=owl_restriction, predicate=OWL.onProperty))
    owl_property = owl_properties[0]
    property = ShaclModelProperty.registry[owl_property]
    owl_ranges_someValuesFrom = list(ontology.objects(subject=owl_restriction, predicate=OWL.someValuesFrom))
    owl_ranges_allValuesFrom = list(ontology.objects(subject=owl_restriction, predicate=OWL.allValuesFrom))
    owl_ranges_hasValue = list(ontology.objects(subject=owl_restriction, predicate=OWL.hasValue))
    owl_ranges_onClass = list(ontology.objects(subject=owl_restriction, predicate=OWL.onClass))
    owl_ranges_onDataRange = list(ontology.objects(subject=owl_restriction, predicate=OWL.onDataRange))
    owl_ranges_onDatatype = list(ontology.objects(subject=owl_restriction, predicate=OWL.onDatatype))
    owl_ranges_qualifiedCardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.qualifiedCardinality))
    owl_ranges_cardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.cardinality))
    owl_ranges_minCardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.minCardinality))
    owl_ranges_maxCardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.maxCardinality))
    owl_ranges_qualifiedMinCardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.minQualifiedCardinality))
    owl_ranges_qualifiedMaxCardinality = list(ontology.objects(subject=owl_restriction, predicate=OWL.maxQualifiedCardinality))
    
    severity = ShaclSeverity.NOT_SET
    owl_range = None
    cardinality = ShaclModelCardinality()
    create_cardinality_attribute = False
    create_value_attribute = False
    if len(owl_ranges_someValuesFrom) == 1:
        owl_range = owl_ranges_someValuesFrom[0]
        cardinality = ShaclModelCardinality(min=1)
        severity = ShaclSeverity.WARNING
        create_cardinality_attribute = True
    if len(owl_ranges_allValuesFrom) == 1:
        owl_range = owl_ranges_allValuesFrom[0]
        cardinality = ShaclModelCardinality()
        severity = ShaclSeverity.WARNING
        create_cardinality_attribute = True
    if len(owl_ranges_onClass) == 1:
        owl_range = owl_ranges_onClass[0]
    if len(owl_ranges_onDataRange) == 1:
        owl_range = owl_ranges_onDataRange[0]
    if len(owl_ranges_onDatatype) == 1:
        owl_range = owl_ranges_onDatatype[0]
    if len(owl_ranges_hasValue) == 1:
        owl_range = owl_ranges_hasValue[0]
        severity = ShaclSeverity.WARNING
        create_value_attribute = True
    if len(owl_ranges_cardinality) == 1:
        cardinality = ShaclModelCardinality(min=owl_ranges_cardinality[0], max=owl_ranges_cardinality[0])
        owl_range = type(owl_ranges_cardinality[0])
        severity = ShaclSeverity.VIOLATION
        create_cardinality_attribute = True
    if len(owl_ranges_qualifiedCardinality) == 1:
        cardinality = ShaclModelCardinality(min=owl_ranges_qualifiedCardinality[0].value,max=owl_ranges_qualifiedCardinality[0].value)
        severity = ShaclSeverity.VIOLATION
        create_cardinality_attribute = True
    if len(owl_ranges_minCardinality) == 1:
        owl_range = type(owl_ranges_minCardinality[0])
        cardinality = ShaclModelCardinality(min=owl_ranges_minCardinality[0].value)
        severity = ShaclSeverity.WARNING
        create_cardinality_attribute = True
    if len(owl_ranges_maxCardinality) == 1:
        owl_range = type(owl_ranges_maxCardinality[0])
        cardinality = ShaclModelCardinality(max=owl_ranges_maxCardinality[0].value)
        severity = ShaclSeverity.VIOLATION
        create_cardinality_attribute = True
    if len(owl_ranges_qualifiedMinCardinality) == 1:
        cardinality = ShaclModelCardinality(min=owl_ranges_qualifiedMinCardinality[0].value)
        severity = ShaclSeverity.WARNING
        create_cardinality_attribute = True
    if len(owl_ranges_qualifiedMaxCardinality) == 1:
        cardinality = ShaclModelCardinality(max=owl_ranges_qualifiedMaxCardinality[0].value)
        severity = ShaclSeverity.VIOLATION
        create_cardinality_attribute = True
    
    range = process_owl_node_by_type(node=owl_range, ontology=ontology)
    
    if create_cardinality_attribute:
        if cardinality.min == 0:
            severity = ShaclSeverity.INFO
            cardinality = ShaclModelCardinality(min=1)
            
      
    if create_cardinality_attribute:
        return ShaclModelCardinalityRestriction(property=property, range=range, cardinality=cardinality, severity=severity)
    
    if create_value_attribute:
        return ShaclModelValueRestriction(property=property, range=range, severity=severity)
    
    
def generate_shacl_class_from_owl_collecting_node(collecting_node: Node, ontology: Graph) -> ShaclModelCollection:
    owl_unionsOf = list(ontology.objects(subject=collecting_node, predicate=OWL.unionOf))
    owl_intersectionsOf = list(ontology.objects(subject=collecting_node, predicate=OWL.intersectionOf))
    owl_complementsOf = list(ontology.objects(subject=collecting_node, predicate=OWL.complementOf))
    owl_onesOf = list(ontology.objects(subject=collecting_node, predicate=OWL.oneOf))
    owl_withRestrictions = list(ontology.objects(subject=collecting_node, predicate=OWL.withRestrictions))
    data_model_entities = None
    owl_complexity_type = None
    if len(owl_unionsOf) > 0:
        data_model_entities = resolve_collecting_collections(collecting_collections=owl_unionsOf, ontology=ontology)
        owl_complexity_type = OWL.unionOf
    if len(owl_intersectionsOf) > 0:
        data_model_entities = resolve_collecting_collections(collecting_collections=owl_intersectionsOf, ontology=ontology)
        owl_complexity_type = OWL.intersectionOf
    if len(owl_complementsOf) > 0:
        data_model_entities = resolve_collecting_collections(collecting_collections=owl_complementsOf, ontology=ontology)
        owl_complexity_type = OWL.complementOf
    if len(owl_onesOf) > 0:
        data_model_entities = resolve_collecting_collections(collecting_collections=owl_onesOf, ontology=ontology)
        owl_complexity_type = OWL.oneOf
    if len(owl_withRestrictions) > 0:
        data_model_entities = resolve_collecting_collections(collecting_collections=owl_withRestrictions, ontology=ontology)
        owl_complexity_type = OWL.withRestrictions
    if not data_model_entities:
        print('Ignoring a restriction for class', collecting_node, 'whose value is too complex BNode.')
        return ShaclModelCollection()

    shacl_container_class = \
        ShaclModelCollection(
            complexity_type=owl_complexity_type,
            collected_nodes=data_model_entities)
    
    return shacl_container_class


def process_owl_node_by_type(
        node: Node,
        ontology: Graph) -> ShaclModelNode:
    if (node, RDF.type, OWL.Restriction) in ontology:
        shacl_model_attribute = generate_attribute_from_owl_restriction(owl_restriction=node, ontology=ontology)
        return shacl_model_attribute
    
    if isinstance(node, Literal):
        shacl_model_literal = ShaclModelLiteral(value=node)
        return shacl_model_literal
    
    owl_collections = \
        [
            set(ontology.objects(subject=node, predicate=OWL.oneOf)),
            set(ontology.objects(subject=node, predicate=OWL.unionOf)),
            set(ontology.objects(subject=node, predicate=OWL.intersectionOf)),
            set(ontology.objects(subject=node, predicate=OWL.complementOf)),
            set(ontology.objects(subject=node, predicate=OWL.withRestrictions))
        ]
    owl_collection = set().union(*owl_collections)
    if len(owl_collection) > 0:
        shacl_model_attribute = \
            generate_shacl_class_from_owl_collecting_node(
                collecting_node=node,
                ontology=ontology)
        return shacl_model_attribute

    if isinstance(node, URIRef) or node == Literal:
        is_datatype = if_resource_is_datatype(resource=node)
        shacl_model_class = generate_model_class_from_owl_class(owl_identifier=node, is_datatype=is_datatype)
        return shacl_model_class
    
    print('Ignoring node', str(node), 'because of its complexity')
    
    return ShaclModelNode()
    
    
def resolve_collecting_collections(collecting_collections: list, ontology: Graph) -> set:
    shacle_entities = set()
    for collecting_collection in collecting_collections:
        if not isinstance(collecting_collection, list):
            items = set(ontology.items(collecting_collection))
        else:
            items = collecting_collections.copy()
        for item in items:
            shacl_entity = process_owl_node_by_type(node=item, ontology=ontology)
            if shacl_entity is not None:
                shacle_entities.add(shacl_entity)
    return shacle_entities
    
    