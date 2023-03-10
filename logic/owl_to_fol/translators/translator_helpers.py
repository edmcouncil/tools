import logging

from rdflib import URIRef, Graph, RDF, OWL, RDFS, BNode, XSD
from rdflib.term import Node

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.symbol import Symbol
from logic.fol_logic.objects.term import Term
from logic.fol_logic.objects.variable import Variable, TPTP_DEFAULT_LETTER_1, TPTP_DEFAULT_LETTER_2


def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variable=Variable()) -> Formula:
    if __can_uri_be_cast_to_predicate(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=1)
        return \
            AtomicFormula(predicate=predicate, arguments=[variable])
    
    if uri == OWL.NamedIndividual:
        predicate = Predicate.registry[uri]
        return \
            AtomicFormula(predicate=predicate, arguments=[variable])
    
    if uri_is_property(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin=uri, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=[Variable(letter=TPTP_DEFAULT_LETTER_1), Variable(letter=TPTP_DEFAULT_LETTER_2)])
    
    logging.warning(msg='Cannot get formula from ' + str(uri))


def get_fol_symbol_for_owl_node(node: Node, owl_ontology: Graph, arity=1) -> Symbol:
    if (node, RDF.type, OWL.NamedIndividual) in owl_ontology or (node, RDF.type, RDFS.Literal) in owl_ontology:
        if node in Term.registry:
            return Term.registry[node]
        else:
            return Term(origin=node)
    
    if node in Predicate.registry:
        return Predicate.registry[node]
    else:
        return Predicate(origin=node, arity=arity)


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
    
    
def __can_uri_be_cast_to_predicate(uri: URIRef, owl_ontology: Graph) -> bool:
    if uri in XSD:
        return True
    if (uri, RDF.type, RDFS.Datatype) in owl_ontology:
        return True
    if (uri, RDF.type, OWL.Class) in owl_ontology:
        return True
    if (uri, RDF.type, OWL.DataRange) in owl_ontology:
        return True
    if uri == OWL.rational:
        return True
    if uri == OWL.real:
        return True
