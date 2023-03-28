from collections import namedtuple
from importlib.resources import Resource

from rdflib import BNode, Graph, OWL, URIRef, Literal, RDF, RDFS

from compare.compare_code.owl_helpers.restriction_classifier import get_restricting_property, \
    get_restricting_type_and_class, \
    get_restriction_modality_and_cardinality_value

RestrictionTuple = namedtuple('OntologicalType', 'restricting_property restriction_type restricted_class restriction_modality restricted_cardinality')


def identify_restriction(restriction: BNode, ontology: Graph) -> tuple:
    restricting_property = get_restricting_property(restriction=restriction, ontology=ontology)
    restricting_type_and_class = get_restricting_type_and_class(restriction=restriction, ontology=ontology)
    restriction_modality_and_cardinality_value = get_restriction_modality_and_cardinality_value(restriction=restriction, ontology=ontology)
    
    restriction_tuple = \
        RestrictionTuple(
            restricting_property=restricting_property,
            restriction_type=restricting_type_and_class[0],
            restricted_class=restricting_type_and_class[1],
            restriction_modality=restriction_modality_and_cardinality_value[0],
            restricted_cardinality=restriction_modality_and_cardinality_value[1])
    
    return restriction_tuple
    

def identify_datatype_restriction(datatype_restriction: BNode, ontology: Graph) -> tuple:
    restricted_datatypes = list(ontology.objects(subject=datatype_restriction, predicate=OWL.onDatatype))
    for restricted_datatype in restricted_datatypes:
        restricting_restriction = list(ontology.objects(subject=datatype_restriction, predicate=OWL.withRestrictions))
        identified_restricting_restriction = identify_resource(resource=restricting_restriction[0], ontology=ontology)
        return tuple([restricted_datatype, identified_restricting_restriction])
    resource_unions_of = list(ontology.objects(subject=datatype_restriction, predicate=OWL.unionOf))
    if len(resource_unions_of) == 1:
        identified_resource = get_listed_resources(rdf_list_object=resource_unions_of[0], ontology=ontology, rdf_list=list())
        return tuple(identified_resource)
    else:
        identified_resource = identify_collection(resource_unions_of, ontology, OWL.unionOf)
        return identified_resource


def identify_collection(collections: list, ontology: Graph, collection_type) -> tuple:
    identified_collections = list()
    for collection in collections:
        if not isinstance(collection, list):
            items = ontology.items(collection)
        identified_items = list()
        for item in items:
            identified_item = identify_resource(item, ontology)
            identified_items.append(identified_item)
        identified_collection = tuple([collection_type] + identified_items)
        identified_collections.append(identified_collection)
    return tuple(identified_collections)


def identify_resource(resource: Resource, ontology: Graph) -> object:
    identified_resource = None
    
    if isinstance(resource, URIRef) or isinstance(resource, Literal):
        return resource
    
    resource_types = set(ontology.objects(subject=resource, predicate=RDF.type))
    
    if OWL.Restriction in resource_types:
        identified_resource = identify_restriction(restriction=resource, ontology=ontology)
        return identified_resource
    
    if RDFS.Datatype in resource_types:
        identified_resource = identify_datatype_restriction(datatype_restriction=resource, ontology=ontology)
        return identified_resource

    resource_ones_of = set(ontology.objects(subject=resource, predicate=OWL.oneOf))
    if len(resource_ones_of) > 0:
        identified_resource = identify_collection(resource_ones_of, ontology, OWL.oneOf)
        return identified_resource
    
    resource_unions_of = set(ontology.objects(subject=resource, predicate=OWL.unionOf))
    if len(resource_unions_of) > 0:
        identified_resource = identify_collection(resource_unions_of, ontology, OWL.unionOf)
        return identified_resource
    
    resource_intersections_of = set(ontology.objects(subject=resource, predicate=OWL.intersectionOf))
    if len(resource_intersections_of) > 0:
        identified_resource = identify_collection(resource_intersections_of, ontology, OWL.intersectionOf)
        return identified_resource
    
    resource_complements_of = set(ontology.objects(subject=resource, predicate=OWL.complementOf))
    if len(resource_complements_of) > 0:
        identified_resource = identify_collection(resource_complements_of, ontology, OWL.complementOf)
        return identified_resource
    
    resource_subject_predicates = list(ontology.subject_predicates(object=resource))
    if len(resource_subject_predicates) > 0:
        for resource_subject_predicate in resource_subject_predicates:
            if resource_subject_predicate[1] == OWL.propertyChainAxiom:
                chained_properties = get_listed_resources(rdf_list_object=resource, ontology=ontology, rdf_list=list())
                return chained_properties
            if resource_subject_predicate[1] == OWL.withRestrictions:
                datatype_restrictions = get_listed_resources(rdf_list_object=resource, ontology=ontology, rdf_list=list())
                identified_resource = identify_collection(datatype_restrictions, ontology, OWL.withRestrictions)
                return identified_resource
    
    return identified_resource


def get_listed_resources(rdf_list_object: Resource, ontology: Graph, rdf_list: list) -> list:
    first_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return rdf_list
    rdf_list.append(first_items_in_rdf_list[0])
    rest_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.rest))
    rdf_list = get_listed_resources(rdf_list_object=rest_items_in_rdf_list[0], ontology=ontology, rdf_list=rdf_list)
    return rdf_list