import logging

from rdflib import URIRef, Graph, RDF, OWL, RDFS, BNode, XSD, Literal
from rdflib.term import Node, Identifier

from logic.fol_logic.objects.atomic_formula import AtomicFormula
from logic.fol_logic.objects.constant_term import ConstantTerm
from logic.fol_logic.objects.formula import Formula
from logic.fol_logic.objects.predicate import Predicate
from logic.fol_logic.objects.symbol import Symbol
from logic.fol_logic.objects.term import Term
from logic.owl_to_fol.translators.formula_origin_registry import FormulaOriginRegistry
from logic.owl_to_fol.translators.translator_maps import SW_TO_PYTHON_DATATYPE_MAP


def get_subformula_from_uri(uri: URIRef, owl_ontology: Graph, variables: list) -> Formula:
    if __can_uri_be_cast_to_unary_predicate(uri=uri, rdf_graph=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin_value=uri, arity=1)
        return \
            AtomicFormula(predicate=predicate, arguments=variables[:1])
    
    if __can_uri_be_cast_to_binary_predicate(uri=uri, owl_ontology=owl_ontology):
        if uri in Predicate.registry:
            predicate = Predicate.registry[uri]
        else:
            predicate = Predicate(origin_value=uri, arity=2)
        return \
            AtomicFormula(predicate=predicate, arguments=variables)
    
    if __can_uri_be_cast_to_term(uri=uri, owl_ontology=owl_ontology):
        if uri in Term.registry:
            term = Term.registry[uri]
        else:
            term = Term(origin_value=uri)
        return term
    
    logging.warning(msg='Cannot get formula from ' + str(uri))


def get_fol_symbol_for_owl_node(identifier: Identifier, rdf_graph: Graph, arity=1) -> Symbol:
    if (identifier, RDF.type, OWL.NamedIndividual) in rdf_graph:
        if identifier in ConstantTerm.registry:
            return ConstantTerm.registry[identifier]
        else:
            return ConstantTerm(origin_value=identifier)
        
    if isinstance(identifier, Literal):
        if identifier in ConstantTerm.registry:
            return ConstantTerm.registry[identifier]
        else:
            if identifier.datatype in SW_TO_PYTHON_DATATYPE_MAP:
                origin_value = identifier.value
                origin_type = SW_TO_PYTHON_DATATYPE_MAP[identifier.datatype]
            else:
                origin_value = str(identifier.value)
                origin_type = str
            term = ConstantTerm(origin_value=origin_value, origin_type=origin_type)
            FormulaOriginRegistry.literals_map[identifier] = term
            return term
        
    # if (identifier, RDF.type, RDFS.Literal) in rdf_graph:
    #     if identifier in ConstantTerm.registry:
    #         return ConstantTerm.registry[identifier]
    #     else:
    #         return ConstantTerm(origin_value=identifier)
        
    if __can_uri_be_cast_to_unary_predicate(uri=identifier, rdf_graph=rdf_graph) or __can_uri_be_cast_to_binary_predicate(uri=identifier, owl_ontology=rdf_graph):
        if identifier in Predicate.registry:
            return Predicate.registry[identifier]
        else:
            return Predicate(origin_value=identifier, arity=arity)
    
    


def __can_uri_be_cast_to_binary_predicate(uri: Node, owl_ontology: Graph) -> bool:
    if (uri, RDF.type, OWL.ObjectProperty) in owl_ontology:
        return True
    if (uri, RDF.type, OWL.DatatypeProperty) in owl_ontology:
        return True
    if (uri, RDF.type, RDF.Property) in owl_ontology:
        return True
    return False


def __can_uri_be_cast_to_unary_predicate(uri: URIRef, rdf_graph: Graph) -> bool:
    if uri in XSD:
        return True
    if (uri, RDF.type, RDFS.Datatype) in rdf_graph:
        return True
    if (uri, RDF.type, RDFS.Class) in rdf_graph:
        return True
    if (uri, RDF.type, OWL.Class) in rdf_graph:
        return True
    if (uri, RDF.type, OWL.DataRange) in rdf_graph:
        return True
    if uri == OWL.rational:
        return True
    if uri == OWL.real:
        return True
    if uri == OWL.Thing:
        return True
    return False


def __can_uri_be_cast_to_term(uri: URIRef, owl_ontology: Graph) -> bool:
    if len(set(owl_ontology.predicate_objects(subject=uri))) > 0:
        return True
    else:
        return True


