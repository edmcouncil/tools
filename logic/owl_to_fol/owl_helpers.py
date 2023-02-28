from rdflib import Graph, RDF, OWL
from rdflib.resource import Resource
from rdflib.term import Node, BNode


def uri_is_property(uri: Node, owl_ontology: Graph) -> bool:
    if (uri, RDF.type, OWL.ObjectProperty) in owl_ontology:
        return True
    if (uri, RDF.type, OWL.DatatypeProperty) in owl_ontology:
        return True
    if (uri, RDF.type, RDF.Property) in owl_ontology:
        return True
    return False

def try_to_cast_bnode_as_typed_list(bnode: BNode, owl_ontology: Graph) -> tuple:
    owl_unions = list(owl_ontology.objects(subject=bnode, predicate=OWL.unionOf))
    if len(owl_unions) > 0:
        return OWL.unionOf, owl_unions[0]

    owl_intersections = list(owl_ontology.objects(subject=bnode, predicate=OWL.intersectionOf))
    if len(owl_intersections) > 0:
        return OWL.intersectionOf, owl_intersections[0]

    owl_complements = list(owl_ontology.objects(subject=bnode, predicate=OWL.complementOf))
    if len(owl_complements) > 0:
        return OWL.complementOf, owl_complements[0]
    
def get_listed_resources(rdf_list_object: Resource, ontology: Graph, rdf_list: list) -> list:
    first_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.first))
    if len(first_items_in_rdf_list) == 0:
        return rdf_list
    rdf_list.append(first_items_in_rdf_list[0])
    rest_items_in_rdf_list = list(ontology.objects(subject=rdf_list_object, predicate=RDF.rest))
    rdf_list = get_listed_resources(rdf_list_object=rest_items_in_rdf_list[0], ontology=ontology, rdf_list=rdf_list)
    return rdf_list