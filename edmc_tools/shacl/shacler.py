from rdflib import RDFS, Graph, URIRef, RDF, BNode, OWL
from rdflib import SH
from rdflib.collection import Collection
from rdflib.term import Literal, Node

from shacl.objects.shacl_model_cardinality_restriction import ShaclModelCardinalityRestriction
from shacl.objects.shacl_model_class import ShaclModelIdentifiedClass
from shacl.objects.shacl_model_container_class import ShaclModelContainerClass
from shacl.objects.shacl_model_restriction import ShaclModelRestriction
from shacl.objects.shacl_model_value_attribute import ShaclModelValueRestriction


def shacl() -> Graph:
    shacled_ontology = Graph()
    shacled_ontology.bind('sh',SH)
    for data_model_class in ShaclModelIdentifiedClass.registry.values():
        if data_model_class.is_leaf:
            shacl_class(data_model_class=data_model_class, shacled_ontology=shacled_ontology)
    return shacled_ontology


def shacl_class(data_model_class: ShaclModelIdentifiedClass, shacled_ontology: Graph):
    if len(data_model_class.attributes) > 0:
        owl_class = data_model_class.iri
        shacl_string_for_shape = str(owl_class) + 'Shape'
        shacl_shape_iri = URIRef(shacl_string_for_shape)
        
        shacled_ontology.add((shacl_shape_iri, RDF.type, SH.NodeShape))
        shacled_ontology.add((shacl_shape_iri, SH.targetClass, owl_class))
        
        for attribute in data_model_class.attributes:
            if isinstance(attribute, ShaclModelRestriction):
                shacl_restriction(
                    restriction=attribute,
                    shacled_ontology=shacled_ontology,
                    shacl_component=shacl_shape_iri)
                
    
def shacl_restriction(restriction: ShaclModelRestriction, shacled_ontology: Graph, shacl_component: Node):
    constraint = BNode()
    shacled_ontology.add((constraint, SH.path, restriction.property.iri))
    if isinstance(restriction, ShaclModelCardinalityRestriction):
        constraint = shacl_cardinality_restriction(restriction=restriction, shacled_ontology=shacled_ontology, constraint=constraint)
    if isinstance(restriction, ShaclModelValueRestriction):
        constraint = shacl_value_restriction(restriction=restriction, shacled_ontology=shacled_ontology, constraint=constraint)
    shacled_ontology.add((constraint, SH.severity, restriction.severity.value))
    shacled_ontology.add((shacl_component, SH.property, constraint))
    return constraint
    
    
def shacl_cardinality_restriction(restriction: ShaclModelCardinalityRestriction, shacled_ontology: Graph, constraint: BNode) -> BNode:
    if isinstance(restriction.range, ShaclModelContainerClass):
        shacl_container_class(container_class=restriction.range, shacled_ontology=shacled_ontology, parent_component=constraint)
    else:
        if isinstance(restriction.range, ShaclModelRestriction):
            shacl_restriction(restriction=restriction.range,shacled_ontology=shacled_ontology, shacl_component=constraint)
            # shacled_ontology.add((constraint, URIRef(str(SH) + 'class'), owl_range))
        else:
            owl_range = restriction.range.iri
            if owl_range == Literal:
                shacled_ontology.add((constraint, SH.nodeKind, RDFS.Literal))
            else:
                if restriction.range.is_datatype:
                    shacled_ontology.add((constraint, URIRef(str(SH)+'datatype'), owl_range))
                else:
                    shacled_ontology.add((constraint,  URIRef(str(SH)+'class'), owl_range))
    if restriction.cardinality.min > -1:
        shacled_ontology.add((constraint,SH.minCount,Literal(restriction.cardinality.min)))
    if restriction.cardinality.max > -1:
        shacled_ontology.add((constraint, SH.maxCount, Literal(restriction.cardinality.max)))
        
    return constraint
    
    
def shacl_value_restriction(restriction: ShaclModelValueRestriction, shacled_ontology: Graph, constraint: BNode) -> BNode:
    shacled_ontology.add((constraint, SH.hasValue, restriction.range.iri))
    return constraint

    
def shacl_container_class(container_class: ShaclModelContainerClass, shacled_ontology: Graph, parent_component: BNode) -> BNode:
    shacl_complexity_type = None
    if container_class.complexity_type == OWL.intersectionOf:
        shacl_complexity_type = URIRef(str(SH)+'or')
    if container_class.complexity_type == OWL.unionOf:
        shacl_complexity_type = URIRef(str(SH)+'or')
    if container_class.complexity_type == OWL.complementOf:
        shacl_complexity_type = URIRef(str(SH)+'not')
    if not shacl_complexity_type:
        print('Cannot process attribute', str(container_class))
    contained_owl_classes = list()
    shacl_collection_node = BNode()
    for shacl_entity in container_class.constituting_attributes:
        if isinstance(shacl_entity, ShaclModelContainerClass):
            contained_owl_class = shacl_container_class(container_class=shacl_entity, shacled_ontology=shacled_ontology,parent_component=shacl_collection_node)
        else:
            contained_owl_class = shacl_entity
        contained_owl_classes.append(contained_owl_class.iri)
        
    Collection(shacled_ontology, shacl_collection_node, contained_owl_classes)
    shacled_ontology.add((parent_component,shacl_complexity_type,shacl_collection_node))
    return parent_component
    