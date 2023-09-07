import logging

from rdflib import Graph, RDF, RDFS, OWL, DC
from rdflib.term import Identifier, URIRef

IGNORED_SW_PREDICATES = \
    {
        OWL.onProperty,
        OWL.onClass,
        OWL.someValuesFrom,
        OWL.allValuesFrom,
        OWL.cardinality,
        OWL.minCardinality,
        OWL.maxCardinality,
        OWL.minQualifiedCardinality,
        OWL.maxQualifiedCardinality,
        OWL.hasValue
    }

OUT_OF_SCOPE_SW_TYPES = \
    {
        RDF.Property,
        RDFS.Resource,
        OWL.Class,
        OWL.ObjectProperty,
        OWL.DatatypeProperty,
        OWL.AnnotationProperty,
        OWL.Ontology
    }


def is_triple_out_of_scope(sw_triple, rdf_graph: Graph) -> bool:
    sw_triple_subject = sw_triple[0]
    sw_triple_predicate = sw_triple[1]
    sw_triple_object = sw_triple[2]
    
    rdf_triple_subject_is_out_of_scope = is_node_out_of_scope(node=sw_triple_subject, owl_ontology=rdf_graph)
    if rdf_triple_subject_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_subject) + ' as the subject')
        return True
    
    rdf_triple_predicate_is_out_of_scope = is_node_out_of_scope(node=sw_triple_predicate, owl_ontology=rdf_graph)
    if rdf_triple_predicate_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_predicate) + ' as the predicate')
        return True
    
    rdf_triple_object_is_out_of_scope = is_node_out_of_scope(node=sw_triple_object, owl_ontology=rdf_graph)
    if rdf_triple_object_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_object) + ' as the object')
        return True
        
    if sw_triple_predicate == RDF.type and sw_triple_object in OUT_OF_SCOPE_SW_TYPES:
        logging.info('Dropping an out-of scope triple ' + str(sw_triple))
        return True
    return False


def is_ignored_triple(sw_triple: tuple) -> bool:
    sw_predicate = sw_triple[1]
    if sw_predicate in IGNORED_SW_PREDICATES:
        return True
    return False


def is_node_out_of_scope(node: Identifier, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.AnnotationProperty) in owl_ontology:
        return True
    if node == OWL.deprecated:
        return True
    if node == URIRef('http://www.w3.org/2002/07/owl'):
        return True
    if node == OWL.NamedIndividual:
        return True
    if node == OWL.Ontology:
        return True
    if node in DC:
        return True
    return False