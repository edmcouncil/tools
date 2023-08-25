import logging

from rdflib import Graph, RDF, RDFS, OWL
from rdflib.term import Identifier

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


def is_triple_out_of_scope(sw_triple, rdf_graph: Graph) -> bool:
    sw_triple_subject = sw_triple[0]
    sw_triple_predicate = sw_triple[1]
    sw_triple_object = sw_triple[2]
    
    rdf_triple_subject_is_out_of_scope = node_is_out_of_scope(node=sw_triple_subject, owl_ontology=rdf_graph)
    if rdf_triple_subject_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_subject) + ' as the subject')
        return True
    
    rdf_triple_predicate_is_out_of_scope = node_is_out_of_scope(node=sw_triple_predicate, owl_ontology=rdf_graph)
    if rdf_triple_predicate_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_predicate) + ' as the predicate')
        return True
    
    rdf_triple_object_is_out_of_scope = node_is_out_of_scope(node=sw_triple_object, owl_ontology=rdf_graph)
    if rdf_triple_object_is_out_of_scope:
        logging.info('Dropping a out-of scope triple with ' + str(sw_triple_object) + ' as the object')
        return True
        
    if sw_triple[1] == RDF.type and (sw_triple[2] in RDF or sw_triple[2] in RDFS or sw_triple[2] in OWL):
        logging.info('Dropping an out-of scope triple ' + str(sw_triple))
        return True
    return False


def is_ignored_triple(sw_triple: tuple) -> bool:
    sw_predicate = sw_triple[1]
    if sw_predicate in IGNORED_SW_PREDICATES:
        return True
    return False


def node_is_out_of_scope(node: Identifier, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.Ontology) in owl_ontology:
        return True
    if (node, RDF.type, OWL.AnnotationProperty) in owl_ontology:
        return True
    
    return False