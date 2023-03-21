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

    if rdf_triple[1] == RDF.type and rdf_triple[2] == RDF.Property:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == RDF.List:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == RDFS.Datatype:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Class:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.Restriction:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.ObjectProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.DatatypeProperty:
        return True
    if rdf_triple[1] == RDF.type and rdf_triple[2] == OWL.AllDifferent:
        return True
    
    if rdf_triple[1] == RDF.type:
        return False
    if rdf_triple[1] == RDFS.subClassOf:
        return False
    if rdf_triple[1] == RDFS.subPropertyOf:
        return False
    if rdf_triple[1] == RDFS.domain:
        return False
    if rdf_triple[1] == RDFS.range:
        return False
    if rdf_triple[1] == OWL.equivalentClass:
        return False
    if rdf_triple[1] == OWL.equivalentProperty:
        return False
    if rdf_triple[1] == OWL.disjointWith:
        return False
    if rdf_triple[1] == OWL.propertyDisjointWith:
        return False
    if rdf_triple[1] == OWL.disjointUnionOf:
        return False
    if rdf_triple[1] == OWL.sameAs:
        return False
    if rdf_triple[1] == OWL.distinctMembers:
        return False
    if rdf_triple[1] == OWL.complementOf:
        return False
    if rdf_triple[1] == OWL.inverseOf:
        return False
    if rdf_triple[1] == OWL.propertyChainAxiom:
        return False
    
    if rdf_triple[1] not in RDF and rdf_triple[1] not in RDFS and rdf_triple[1] not in OWL:
        return False
    
    # if rdf_triple[1] == RDF.first:
    #     return True
    # if rdf_triple[1] == RDF.rest:
    #     return True
    # if rdf_triple[1] == RDFS.isDefinedBy:
    #     return True
    # if rdf_triple[1] == RDFS.seeAlso:
    #     return True
    # if rdf_triple[1] == OWL.unionOf:
    #     return True
    # if rdf_triple[1] == OWL.intersectionOf:
    #     return True
    # if rdf_triple[1] == OWL.complementOf:
    #     return True
    # if rdf_triple[1] == OWL.oneOf:
    #     return True
    # if rdf_triple[1] == OWL.onClass:
    #     return True
    # if rdf_triple[1] == OWL.onDatatype:
    #     return True
    # if rdf_triple[1] == OWL.onDataRange:
    #     return True
    # if rdf_triple[1] == OWL.onProperty:
    #     return True
    # if rdf_triple[1] == OWL.imports:
    #     return True
    #
    return True
