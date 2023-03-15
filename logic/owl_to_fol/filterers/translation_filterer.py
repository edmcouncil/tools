from rdflib import Graph, RDF, OWL, Literal, RDFS
from rdflib.term import Node


def node_is_out_of_scope(node: Node, owl_ontology: Graph) -> bool:
    if (node, RDF.type, OWL.Ontology) in owl_ontology:
        return True
    if (node, RDF.type, OWL.AnnotationProperty) in owl_ontology:
        return True
    if isinstance(node, Literal):
        return True
    return False


def triple_is_of_of_scope(rdf_triple: tuple) -> bool:
    if rdf_triple[0] in RDF:
        return True
    if rdf_triple[0] in RDFS:
        return True
    if rdf_triple[0] in OWL:
        return True
    
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Class:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Restriction:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.ObjectProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.DatatypeProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == RDF.Property:
        return True
    if rdf_triple[1] == OWL.imports:
        return True
    
    if rdf_triple[1] == RDFS.isDefinedBy:
        return True
    if rdf_triple[1] == RDFS.seeAlso:
        return True
    
    if rdf_triple[1] == OWL.unionOf:
        return True
    if rdf_triple[1] == OWL.intersectionOf:
        return True
    if rdf_triple[1] == OWL.complementOf:
        return True
    if rdf_triple[1] == OWL.oneOf:
        return True
    
    return False
